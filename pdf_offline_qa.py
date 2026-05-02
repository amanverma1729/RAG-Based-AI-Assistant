


import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import re
import time
import textwrap
import json
import requests
from pathlib import Path
import numpy as np
import pypdf
import pdfplumber
from sklearn.metrics.pairwise import cosine_similarity

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MAX_PDFS     = 5
APP_TITLE    = "PDF Intelligence Pro — Offline"
CHUNK_SIZE   = 400      # words per chunk
CHUNK_OVERLAP= 80       # overlap between chunks
TOP_K_CHUNKS = 6        # kitne relevant chunks use karo answer ke liye
OLLAMA_URL   = "http://localhost:11434"

COLORS = {
    "bg_dark":       "#0D0F1A",
    "bg_card":       "#161929",
    "bg_sidebar":    "#0F1120",
    "accent_blue":   "#4F7FFF",
    "accent_purple": "#9B72F5",
    "accent_green":  "#22D3A0",
    "accent_red":    "#F87171",
    "accent_orange": "#FBBF24",
    "accent_cyan":   "#22D3EE",
    "text_primary":  "#E8EEFF",
    "text_secondary":"#7B8DB0",
    "border":        "#252A45",
    "user_bubble":   "#1A2E50",
    "ai_bubble":     "#161929",
    "input_bg":      "#1A1E30",
    "thinking":      "#2D1F45",
}

PDF_COLORS = ["#4F7FFF","#9B72F5","#22D3A0","#FBBF24","#F87171"]


class OfflineAIEngine:
    

    def __init__(self, status_callback=None):
        self.status_cb  = status_callback or (lambda msg, color: None)
        self.model      = None          # sentence-transformers model
        self.pdf_data   = {}            # slot_index -> {chunks, embeddings, meta}
        self.model_name = "all-MiniLM-L6-v2"
        self._model_loading = False
        self.ollama_model = None        # detected ollama model name

    
    def load_model(self, done_callback):
        """Background mein sentence-transformer model load karo."""
        if self.model is not None:
            done_callback(True, "Model already loaded")
            return
        self._model_loading = True

        def worker():
            try:
                self.status_cb("🔄 AI model download/load ho raha hai (80MB, sirf pehli baar)...", "orange")
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                self._model_loading = False
                done_callback(True, "Model ready!")
            except Exception as e:
                self._model_loading = False
                done_callback(False, str(e))

        threading.Thread(target=worker, daemon=True).start()

   
    def index_pdf(self, slot_index: int, pdf_path: str, done_callback):
        """PDF load + chunk + embed — background mein."""
        def worker():
            try:
                # 1. Extract text
                text, pages = self._extract_text(pdf_path)

                # 2. Split into chunks
                chunks = self._make_chunks(text)

                # 3. Create embeddings
                if self.model is None:
                    done_callback(False, slot_index, "Model abhi load nahi hua!")
                    return

                embeddings = self.model.encode(
                    [c["text"] for c in chunks],
                    show_progress_bar=False,
                    batch_size=32
                )

                self.pdf_data[slot_index] = {
                    "path":       pdf_path,
                    "filename":   Path(pdf_path).name,
                    "pages":      pages,
                    "chunks":     chunks,
                    "embeddings": embeddings,
                    "size_kb":    os.path.getsize(pdf_path) // 1024,
                    "total_chunks": len(chunks)
                }
                done_callback(True, slot_index, f"{len(chunks)} chunks, {pages} pages")
            except Exception as e:
                done_callback(False, slot_index, str(e))

        threading.Thread(target=worker, daemon=True).start()

    
    def answer(self, question: str, active_slots: list[int], done_callback):
        """Question ka answer dho — background mein."""
        def worker():
            try:
                if self.model is None:
                    done_callback("❌ AI model load nahi hua abhi tak. Thoda wait karo.")
                    return

                
                q_embedding = self.model.encode([question])[0]

                
                all_chunks = []
                for slot in active_slots:
                    if slot not in self.pdf_data:
                        continue
                    data = self.pdf_data[slot]
                    sims = cosine_similarity([q_embedding], data["embeddings"])[0]
                    top_indices = np.argsort(sims)[::-1][:TOP_K_CHUNKS]

                    for idx in top_indices:
                        if sims[idx] > 0.15:  # minimum relevance threshold
                            all_chunks.append({
                                "text":     data["chunks"][idx]["text"],
                                "page":     data["chunks"][idx]["page"],
                                "filename": data["filename"],
                                "score":    float(sims[idx]),
                                "slot":     slot
                            })

                if not all_chunks:
                    done_callback("🔍 Is sawaal ka jawab loaded PDFs mein nahi mila.\n\nKuch aur poochho ya alag PDFs load karo.")
                    return

                
                all_chunks.sort(key=lambda x: x["score"], reverse=True)
                top_chunks = all_chunks[:TOP_K_CHUNKS]

                
                ollama_ans = self._try_ollama(question, top_chunks)
                if ollama_ans:
                    done_callback(ollama_ans)
                else:
                    # Smart extractive answer
                    ans = self._build_extractive_answer(question, top_chunks)
                    done_callback(ans)

            except Exception as e:
                done_callback(f"❌ Error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    
    def check_ollama(self) -> tuple[bool, str]:
        """Ollama running hai? Aur kaunsa model available hai?"""
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            if r.status_code == 200:
                models = r.json().get("models", [])
                if models:
                    # Prefer certain models in order
                    preferred = ["llama3","llama3.2","llama3.1","mistral","phi3",
                                 "phi","gemma","neural-chat","qwen"]
                    names = [m["name"] for m in models]
                    for pref in preferred:
                        for n in names:
                            if pref in n.lower():
                                self.ollama_model = n
                                return True, n
                    self.ollama_model = names[0]
                    return True, names[0]
                return True, "No models pulled"
        except Exception:
            pass
        return False, "Ollama not running"

    def _try_ollama(self, question: str, chunks: list) -> str | None:
        
        if not self.ollama_model:
            ok, name = self.check_ollama()
            if not ok or "No models" in name:
                return None

        context = self._build_context(chunks)
        prompt = f"""You are a helpful assistant answering questions about PDF documents.

RELEVANT CONTENT FROM PDFs:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based only on the provided content
- Be clear and concise
- Mention which document/page the info came from when relevant
- If answer is not in content, say so clearly
- Respond in the same language as the question (Hindi or English)

ANSWER:"""

        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": self.ollama_model, "prompt": prompt, "stream": False},
                timeout=120
            )
            if r.status_code == 200:
                ans = r.json().get("response", "").strip()
                if ans:
                    return f"🤖 **[Ollama: {self.ollama_model}]**\n\n{ans}"
        except Exception:
            pass
        return None

    
    def _build_extractive_answer(self, question: str, chunks: list) -> str:
       
        lines = ["📖 **Relevant Content Found:**\n"]

        seen_files = {}
        for i, chunk in enumerate(chunks[:4]):
            fname = chunk["filename"]
            page  = chunk["page"]
            score = chunk["score"]
            text  = chunk["text"].strip()

            if fname not in seen_files:
                seen_files[fname] = []
            seen_files[fname].append(i)

            # Highlight karo question ke words
            highlighted = self._highlight_keywords(text, question)

            lines.append(f"━━ 📄 {fname}  |  Page {page}  |  Relevance: {int(score*100)}%")
            lines.append(f"{highlighted}\n")

       
        files_used = list(seen_files.keys())
        lines.append(f"\n💡 **Tip:** Better answers ke liye **Ollama** install karo (ollama.com)")
        lines.append(f"   Phir: `ollama pull llama3.2` — poora AI locally chalega! 🚀")

        return "\n".join(lines)

    def _highlight_keywords(self, text: str, question: str) -> str:
        
        
        stop = {"kya","hai","ka","ke","ki","mein","se","ko","tha","the","hain",
                "what","is","the","a","an","of","in","to","for","and","or","how",
                "when","where","who","which","tell","me","about","please"}
        words = [w.lower().strip("?.,!") for w in question.split() if w.lower() not in stop and len(w) > 2]

        # Wrap keywords in [[ ]] for visual emphasis (CTk doesn't support HTML)
        result = text
        for word in words[:5]:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result  = pattern.sub(f"»{word}«", result, count=3)
        return result

    
    def _extract_text(self, pdf_path: str) -> tuple[str, int]:
        
        pages_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    t = page.extract_text()
                    if t and t.strip():
                        pages_text.append((i + 1, t.strip()))
            if pages_text:
                return pages_text, len(pages_text)
        except Exception:
            pass

       
        try:
            reader = pypdf.PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                t = page.extract_text()
                if t and t.strip():
                    pages_text.append((i + 1, t.strip()))
        except Exception:
            pass

        return pages_text, len(pages_text)

    def _make_chunks(self, pages_text) -> list[dict]:
       
        chunks = []
        for page_num, text in pages_text:
            words = text.split()
            i = 0
            while i < len(words):
                chunk_words = words[i : i + CHUNK_SIZE]
                chunk_text  = " ".join(chunk_words)
                if len(chunk_text.strip()) > 50:
                    chunks.append({"text": chunk_text, "page": page_num})
                i += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def _build_context(self, chunks: list) -> str:
        parts = []
        for chunk in chunks:
            parts.append(f"[From: {chunk['filename']}, Page {chunk['page']}]\n{chunk['text']}")
        return "\n\n---\n\n".join(parts)

    def remove_pdf(self, slot_index: int):
        self.pdf_data.pop(slot_index, None)


class PDFOfflineApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1320x840")
        self.minsize(1050, 720)
        self.configure(fg_color=COLORS["bg_dark"])

        self.engine      = OfflineAIEngine(status_callback=self._engine_status)
        self.pdf_slots   = [None] * MAX_PDFS
        self.is_thinking = False

        self._build_ui()
        self._init_engine()

   
    def _init_engine(self):
        
        self.engine.load_model(self._on_model_loaded)

    def _on_model_loaded(self, success: bool, msg: str):
        if success:
            self._engine_status("✅ AI Engine Ready! PDF upload karo.", "green")
            self._check_ollama_status()
        else:
            self._engine_status(f"❌ Model load error: {msg}", "red")

    def _check_ollama_status(self):
        def check():
            ok, name = self.engine.check_ollama()
            if ok and "No models" not in name:
                self.after(0, lambda: self._engine_status(f"🦙 Ollama ready: {name}", "purple"))
                self.after(0, lambda: self.ollama_badge.configure(
                    text=f"🦙 Ollama: {name}", text_color=COLORS["accent_purple"]))
            else:
                self.after(0, lambda: self.ollama_badge.configure(
                    text="🔌 Ollama: Not found (optional)", text_color=COLORS["text_secondary"]))
        threading.Thread(target=check, daemon=True).start()

    def _engine_status(self, msg: str, color: str):
        color_map = {
            "green": COLORS["accent_green"], "red": COLORS["accent_red"],
            "orange": COLORS["accent_orange"], "purple": COLORS["accent_purple"],
            "cyan": COLORS["accent_cyan"]
        }
        c = color_map.get(color, COLORS["text_secondary"])
        self.after(0, lambda: self.status_bar.configure(text=msg, text_color=c))

  
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

   
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=310, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(3, weight=1)

       
        logo_frame = ctk.CTkFrame(sb, fg_color=COLORS["bg_card"], corner_radius=0, height=80)
        logo_frame.grid(row=0, column=0, sticky="ew")
        logo_frame.grid_propagate(False)

        ctk.CTkLabel(logo_frame, text="📄", font=ctk.CTkFont(size=28)).place(x=16, y=14)
        ctk.CTkLabel(logo_frame, text="PDF Intelligence",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"]).place(x=58, y=12)
        ctk.CTkLabel(logo_frame, text="100% OFFLINE • No API Key",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["accent_green"]).place(x=58, y=36)

        self.ollama_badge = ctk.CTkLabel(logo_frame, text="🔄 Checking Ollama...",
            font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"])
        self.ollama_badge.place(x=58, y=55)

      
        info = ctk.CTkFrame(sb, fg_color=COLORS["bg_card"], corner_radius=12)
        info.grid(row=1, column=0, sticky="ew", padx=12, pady=(10, 6))

        self.status_bar = ctk.CTkLabel(info,
            text="🔄 AI model load ho raha hai...",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["accent_orange"],
            wraplength=260, justify="left")
        self.status_bar.pack(padx=12, pady=8)

       
        hdr = ctk.CTkFrame(sb, fg_color="transparent")
        hdr.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 2))
        ctk.CTkLabel(hdr, text="📁 Load PDFs", font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(hdr, text=f"max {MAX_PDFS}", font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]).pack(side="left", padx=6)

       
        scroll = ctk.CTkScrollableFrame(sb, fg_color="transparent",
            scrollbar_button_color=COLORS["border"])
        scroll.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 6))

        self.slot_widgets = []
        for i in range(MAX_PDFS):
            w = self._make_slot(scroll, i)
            w.pack(fill="x", pady=3)
            self.slot_widgets.append(w)

       
        bot = ctk.CTkFrame(sb, fg_color="transparent")
        bot.grid(row=4, column=0, sticky="sew", padx=12, pady=8)

        self.count_lbl = ctk.CTkLabel(bot, text="0 / 5 PDFs loaded",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"])
        self.count_lbl.pack(pady=(0,5))

        ctk.CTkButton(bot, text="🗑  Clear All", height=34, corner_radius=8,
            fg_color=COLORS["bg_card"], hover_color="#2A1515",
            text_color=COLORS["accent_red"], font=ctk.CTkFont(size=12),
            command=self._clear_all).pack(fill="x", pady=(0,4))

        ctk.CTkButton(bot, text="🦙  Recheck Ollama", height=34, corner_radius=8,
            fg_color=COLORS["bg_card"], hover_color="#1A1535",
            text_color=COLORS["accent_purple"], font=ctk.CTkFont(size=12),
            command=self._check_ollama_status).pack(fill="x")

    def _make_slot(self, parent, idx: int) -> ctk.CTkFrame:
        color = PDF_COLORS[idx]
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
            corner_radius=10, border_width=1, border_color=COLORS["border"])

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=7)

        badge = ctk.CTkLabel(row, text=str(idx+1), width=24, height=24,
            fg_color=color, corner_radius=7,
            font=ctk.CTkFont(size=11, weight="bold"), text_color="white")
        badge.grid(row=0, column=0, rowspan=2)

        name_lbl = ctk.CTkLabel(row, text=f"Slot {idx+1} — Empty",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"], anchor="w")
        name_lbl.grid(row=0, column=1, sticky="ew", padx=(8,0))

        info_lbl = ctk.CTkLabel(row, text="+ buton se upload karo",
            font=ctk.CTkFont(size=9), text_color=COLORS["border"], anchor="w")
        info_lbl.grid(row=1, column=1, sticky="ew", padx=(8,0))

        row.grid_columnconfigure(1, weight=1)

        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.grid(row=0, column=2, rowspan=2)

        ctk.CTkButton(btns, text="+", width=26, height=26,
            fg_color=color, hover_color=color,
            font=ctk.CTkFont(size=14, weight="bold"), corner_radius=6,
            command=lambda i=idx: self._load_pdf(i)).pack(side="left", padx=(4,2))

        ctk.CTkButton(btns, text="✕", width=26, height=26,
            fg_color=COLORS["bg_dark"], hover_color="#2D1515",
            text_color=COLORS["accent_red"], font=ctk.CTkFont(size=11),
            corner_radius=6,
            command=lambda i=idx: self._remove_pdf(i)).pack(side="left")

        frame._name = name_lbl
        frame._info = info_lbl
        frame._color = color
        return frame

  
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Topbar
        tb = ctk.CTkFrame(main, fg_color=COLORS["bg_card"], height=56, corner_radius=0)
        tb.grid(row=0, column=0, sticky="ew")
        tb.grid_propagate(False)
        tb.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tb, text="💬  AI Chat — Offline Mode",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]).grid(row=0, column=0, padx=18, pady=14, sticky="w")

        self.mode_badge = ctk.CTkLabel(tb, text="⬤  Initializing",
            font=ctk.CTkFont(size=11), text_color=COLORS["accent_orange"],
            fg_color=COLORS["bg_dark"], corner_radius=20, padx=12, pady=3)
        self.mode_badge.grid(row=0, column=1, sticky="e", padx=15)

        ctk.CTkButton(tb, text="🗑 Clear Chat", width=105, height=30,
            fg_color=COLORS["bg_dark"], hover_color=COLORS["border"],
            text_color=COLORS["text_secondary"], font=ctk.CTkFont(size=11),
            corner_radius=7, command=self._clear_chat).grid(row=0, column=2, padx=(0,14))

        # Chat area
        chat_wrap = ctk.CTkFrame(main, fg_color=COLORS["bg_dark"])
        chat_wrap.grid(row=1, column=0, sticky="nsew", padx=14, pady=(10,0))
        chat_wrap.grid_rowconfigure(0, weight=1)
        chat_wrap.grid_columnconfigure(0, weight=1)

        self.chat_area = ctk.CTkScrollableFrame(chat_wrap,
            fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_blue"])
        self.chat_area.grid(row=0, column=0, sticky="nsew")
        self.chat_area.grid_columnconfigure(0, weight=1)

        self._show_welcome()

       
        inp_bar = ctk.CTkFrame(main, fg_color=COLORS["bg_card"], height=108, corner_radius=0)
        inp_bar.grid(row=2, column=0, sticky="ew", pady=(8,0))
        inp_bar.grid_propagate(False)

        inner = ctk.CTkFrame(inp_bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=11)
        inner.grid_columnconfigure(0, weight=1)

        self.q_input = ctk.CTkTextbox(inner, height=55,
            fg_color=COLORS["input_bg"], border_color=COLORS["border"],
            border_width=1, font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"], wrap="word")
        self.q_input.grid(row=0, column=0, sticky="ew", padx=(0,10))

        PLACEHOLDER = "Apna sawaal yahan likhein... (Hindi ya English dono mein)"
        self.q_input.insert("0.0", PLACEHOLDER)
        self.q_input.configure(text_color=COLORS["text_secondary"])
        self.q_input.bind("<FocusIn>",  lambda e: self._focus_in(PLACEHOLDER))
        self.q_input.bind("<FocusOut>", lambda e: self._focus_out(PLACEHOLDER))
        self.q_input.bind("<Return>",   lambda e: (self._send(), "break")[1])
        self.q_input.bind("<Shift-Return>", lambda e: None)

        self.send_btn = ctk.CTkButton(inner, text="Send ➤",
            width=95, height=55,
            fg_color=COLORS["accent_blue"], hover_color="#3A6AEF",
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=10,
            command=self._send)
        self.send_btn.grid(row=0, column=1)

        ctk.CTkLabel(inner,
            text="Enter = Send  •  Shift+Enter = New line  •  No internet needed!",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]).grid(row=1, column=0, columnspan=2, pady=(5,0))

    
    def _show_welcome(self):
        msg = (
            "🚀 PDF Intelligence Pro — 100% OFFLINE\n\n"
            "✅ Koi API Key NAHI chahiye\n"
            "✅ Koi Internet NAHI chahiye\n"
            "✅ Tera data teri machine pe hi rahega\n\n"
            "KAISE KAAM KARTA HAI:\n"
            "  1. AI model pehli baar sirf 80MB download hoga — phir hamesha offline\n"
            "  2. Left se 1-5 PDF upload karo\n"
            "  3. Sawaal poochho — AI relevant content dhundega\n\n"
            "OPTIONAL UPGRADE:\n"
            "  🦙 Ollama install karo (ollama.com) + 'ollama pull llama3.2'\n"
            "     Full local LLM se aur bhi smart answers milenge!"
        )
        self._bubble(msg, "system")

    
    def _load_pdf(self, idx: int):
        if self.engine.model is None:
            messagebox.showinfo("Wait karo", "AI model abhi load ho raha hai, thoda wait karo!")
            return

        path = filedialog.askopenfilename(
            title=f"Slot {idx+1} ke liye PDF chunein",
            filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        w = self.slot_widgets[idx]
        w._name.configure(text="⏳ Processing...", text_color=COLORS["accent_orange"])
        w._info.configure(text="Text extract + embed ho raha hai...")

        def done(success, slot, msg):
            if success:
                d = self.engine.pdf_data[slot]
                self.pdf_slots[slot] = d
                self.after(0, lambda: self._slot_loaded(slot, d))
            else:
                self.after(0, lambda: self._slot_error(slot, msg))

        self.engine.index_pdf(idx, path, done)

    def _slot_loaded(self, idx, data):
        w   = self.slot_widgets[idx]
        fn  = data["filename"]
        short = fn if len(fn) <= 20 else fn[:17] + "..."
        w._name.configure(text=f"✓ {short}", text_color=PDF_COLORS[idx])
        w._info.configure(text=f"{data['pages']} pages • {data['total_chunks']} chunks • {data['size_kb']}KB",
            text_color=COLORS["text_secondary"])
        w.configure(border_color=PDF_COLORS[idx])
        self._update_count()
        self._bubble(
            f"✅ PDF {idx+1} ready!\n"
            f"📄 {data['filename']}\n"
            f"📃 {data['pages']} pages → {data['total_chunks']} searchable chunks\n\n"
            f"Ab is PDF ke baare mein koi bhi sawaal poochho!",
            "system"
        )
        self.mode_badge.configure(text="⬤  Ready", text_color=COLORS["accent_green"])

    def _slot_error(self, idx, msg):
        w = self.slot_widgets[idx]
        w._name.configure(text=f"❌ Slot {idx+1} — Error", text_color=COLORS["accent_red"])
        w._info.configure(text=msg[:35])
        self._bubble(f"❌ Slot {idx+1} load error:\n{msg}", "system")

    def _remove_pdf(self, idx: int):
        if self.pdf_slots[idx] is None:
            return
        fn = self.pdf_slots[idx]["filename"]
        self.pdf_slots[idx] = None
        self.engine.remove_pdf(idx)
        w = self.slot_widgets[idx]
        w._name.configure(text=f"Slot {idx+1} — Empty", text_color=COLORS["text_secondary"])
        w._info.configure(text="+ button se upload karo", text_color=COLORS["border"])
        w.configure(border_color=COLORS["border"])
        self._update_count()
        self._bubble(f"🗑️ {fn} remove kar diya.", "system")

    def _clear_all(self):
        for i in range(MAX_PDFS):
            self.pdf_slots[i] = None
            self.engine.remove_pdf(i)
            w = self.slot_widgets[i]
            w._name.configure(text=f"Slot {i+1} — Empty", text_color=COLORS["text_secondary"])
            w._info.configure(text="+ button se upload karo", text_color=COLORS["border"])
            w.configure(border_color=COLORS["border"])
        self._update_count()
        self._bubble("🗑️ Saare PDFs remove kar diye gaye.", "system")

    def _update_count(self):
        n = sum(1 for s in self.pdf_slots if s is not None)
        self.count_lbl.configure(
            text=f"{n} / {MAX_PDFS} PDFs loaded",
            text_color=COLORS["accent_green"] if n > 0 else COLORS["text_secondary"])

    # ── Chat ──────────────────────────────────────────────────────────────────
    def _focus_in(self, placeholder):
        if self.q_input.get("0.0","end").strip() == placeholder:
            self.q_input.delete("0.0","end")
            self.q_input.configure(text_color=COLORS["text_primary"])

    def _focus_out(self, placeholder):
        if not self.q_input.get("0.0","end").strip():
            self.q_input.insert("0.0", placeholder)
            self.q_input.configure(text_color=COLORS["text_secondary"])

    def _send(self):
        if self.is_thinking:
            return

        q = self.q_input.get("0.0","end").strip()
        placeholder = "Apna sawaal yahan likhein... (Hindi ya English dono mein)"
        if not q or q == placeholder:
            self.q_input.configure(border_color=COLORS["accent_red"])
            self.after(600, lambda: self.q_input.configure(border_color=COLORS["border"]))
            return

        active = [i for i, s in enumerate(self.pdf_slots) if s is not None]
        if not active:
            messagebox.showinfo("PDF Nahi Hai", "Pehle kam se kam 1 PDF load karo!")
            return

        self.q_input.delete("0.0","end")
        self._bubble(q, "user")

        self.is_thinking = True
        self.send_btn.configure(state="disabled", text="⏳")
        self.mode_badge.configure(text="⬤  Thinking...", text_color=COLORS["accent_orange"])

        t_id = self._bubble_thinking()

        def done(answer):
            self.after(0, lambda: self._finish(t_id, answer))

        self.engine.answer(q, active, done)

    def _finish(self, t_id, answer):
        self._remove_thinking(t_id)
        self._bubble(answer, "ai")
        self.is_thinking = False
        self.send_btn.configure(state="normal", text="Send ➤")
        self.mode_badge.configure(text="⬤  Ready", text_color=COLORS["accent_green"])
        self._scroll_bottom()

    # ── Bubble Rendering ──────────────────────────────────────────────────────
    def _bubble(self, text: str, sender: str) -> str:
        f = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        f.pack(fill="x", padx=8, pady=5)
        bid = f"b{int(time.time()*1000)}"
        f._bid = bid

        clean = self._clean(text)

        if sender == "user":
            out = ctk.CTkFrame(f, fg_color="transparent")
            out.pack(anchor="e")
            ctk.CTkLabel(out, text="👤 You", font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COLORS["accent_blue"]).pack(anchor="e", padx=4)
            bub = ctk.CTkFrame(out, fg_color=COLORS["user_bubble"], corner_radius=14)
            bub.pack(anchor="e")
            ctk.CTkLabel(bub, text=clean, font=ctk.CTkFont(size=13),
                text_color=COLORS["text_primary"],
                wraplength=580, justify="left", padx=14, pady=9).pack()

        elif sender == "ai":
            out = ctk.CTkFrame(f, fg_color="transparent")
            out.pack(anchor="w", fill="x")
            ctk.CTkLabel(out, text="🤖 PDF AI (Offline)",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COLORS["accent_purple"]).pack(anchor="w", padx=4)
            bub = ctk.CTkFrame(out, fg_color=COLORS["ai_bubble"],
                corner_radius=14, border_width=1, border_color=COLORS["border"])
            bub.pack(anchor="w", fill="x")
            ctk.CTkLabel(bub, text=clean, font=ctk.CTkFont(size=13),
                text_color=COLORS["text_primary"],
                wraplength=760, justify="left",
                padx=14, pady=11, anchor="w").pack(fill="x")

        elif sender == "system":
            bub = ctk.CTkFrame(f, fg_color=COLORS["bg_card"],
                corner_radius=10, border_width=1, border_color=COLORS["border"])
            bub.pack(fill="x")
            ctk.CTkLabel(bub, text=clean, font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
                wraplength=820, justify="left",
                padx=14, pady=9, anchor="w").pack(fill="x")

        self._scroll_bottom()
        return bid

    def _bubble_thinking(self) -> str:
        f = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        f.pack(fill="x", padx=8, pady=5)
        bid = f"thinking_{int(time.time()*1000)}"
        f._bid = bid
        self._thinking_frame = f

        out = ctk.CTkFrame(f, fg_color="transparent")
        out.pack(anchor="w")
        ctk.CTkLabel(out, text="🤖 PDF AI (Offline)",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["accent_purple"]).pack(anchor="w", padx=4)
        bub = ctk.CTkFrame(out, fg_color=COLORS["thinking"],
            corner_radius=14, border_width=1, border_color=COLORS["accent_purple"])
        bub.pack(anchor="w")
        self._t_lbl = ctk.CTkLabel(bub, text="🔍 Relevant content dhund raha hoon...",
            font=ctk.CTkFont(size=13), text_color=COLORS["accent_purple"],
            padx=14, pady=10)
        self._t_lbl.pack()
        self._animate_thinking()
        self._scroll_bottom()
        return bid

    def _animate_thinking(self):
        if not self.is_thinking:
            return
        frames = [
            "🔍 PDFs mein dhund raha hoon...",
            "🧠 Embeddings compare kar raha hoon...",
            "📊 Relevant chunks nikal raha hoon...",
            "✍️  Answer bana raha hoon...",
        ]
        n = getattr(self,"_tf",0)
        try: self._t_lbl.configure(text=frames[n % len(frames)])
        except: return
        self._tf = n + 1
        self.after(600, self._animate_thinking)

    def _remove_thinking(self, bid):
        try: self._thinking_frame.destroy()
        except: pass

    def _clean(self, text: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*",     r"\1", text)
        text = re.sub(r"`([^`]+)`",     r"[\1]", text)
        return text

    def _scroll_bottom(self):
        self.after(120, lambda: self.chat_area._parent_canvas.yview_moveto(1.0))

    def _clear_chat(self):
        for w in self.chat_area.winfo_children():
            w.destroy()
        self._show_welcome()


if __name__ == "__main__":
    app = PDFOfflineApp()
    app.mainloop()
