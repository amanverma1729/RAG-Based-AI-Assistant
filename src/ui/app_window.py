import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from src.config.theme import COLORS
from src.config.settings import APP_TITLE, MAX_PDFS
from src.engine.ai_engine import OfflineAIEngine
from src.ui.components.sidebar import Sidebar
from src.ui.components.chat import ChatArea

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1320x840")
        self.minsize(1050, 720)
        self.configure(fg_color=COLORS["bg_dark"])

        self.engine = OfflineAIEngine(status_callback=self._engine_status)
        self.pdf_slots = [None] * MAX_PDFS
        
        self._build_ui()
        self._init_engine()

    def _init_engine(self):
        self.engine.load_model(self._on_model_loaded)

    def _on_model_loaded(self, success: bool, msg: str):
        if success:
            self._engine_status("✅ AI Engine Ready! Please upload a PDF.", "green")
            self._check_ollama_status()
        else:
            self._engine_status(f"❌ Model load error: {msg}", "red")

    def _check_ollama_status(self):
        def check():
            ok, name = self.engine.check_ollama()
            if ok and "No models" not in name:
                self.after(0, lambda: self._engine_status(f"🦙 Ollama ready: {name}", "purple"))
                self.after(0, lambda: self.sidebar.update_ollama_badge(name, True))
            else:
                self.after(0, lambda: self.sidebar.update_ollama_badge("", False))
        threading.Thread(target=check, daemon=True).start()

    def _engine_status(self, msg: str, color_key: str):
        self.after(0, lambda: self.sidebar.update_status(msg, color_key))

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build Sidebar
        sidebar_callbacks = {
            'load_pdf': self._load_pdf,
            'remove_pdf': self._remove_pdf,
            'clear_all': self._clear_all,
            'recheck_ollama': self._check_ollama_status
        }
        self.sidebar = Sidebar(self, sidebar_callbacks)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Build Main Area
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

        # Chat Area
        chat_wrap = ctk.CTkFrame(main, fg_color=COLORS["bg_dark"])
        chat_wrap.grid(row=1, column=0, sticky="nsew", padx=14, pady=(10,0))
        chat_wrap.grid_rowconfigure(0, weight=1)
        chat_wrap.grid_columnconfigure(0, weight=1)

        self.chat_area = ChatArea(chat_wrap)
        self.chat_area.grid(row=0, column=0, sticky="nsew")

        self._show_welcome()

        # Input Area
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

        PLACEHOLDER = "Type your question here... (Hindi or English)"
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
            "✅ No API Key required\n"
            "✅ No Internet required\n"
            "✅ Your data stays on your machine\n\n"
            "HOW IT WORKS:\n"
            "  1. AI model downloads once (80MB) — then completely offline\n"
            "  2. Upload 1-5 PDFs from the sidebar\n"
            "  3. Ask questions — AI finds the relevant content\n\n"
            "OPTIONAL UPGRADE:\n"
            "  🦙 Install Ollama (ollama.com) + 'ollama pull llama3.2'\n"
            "     Provides incredibly smart answers using a full local LLM!"
        )
        self.chat_area.add_message(msg, "system")

    def _load_pdf(self, idx: int):
        if self.engine.model is None:
            messagebox.showinfo("Please wait", "AI model is still loading!")
            return

        path = filedialog.askopenfilename(
            title=f"Select PDF for Slot {idx+1}",
            filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        slot_widget = self.sidebar.get_slot(idx)
        slot_widget.set_loading()

        def done(success, slot, msg):
            if success:
                d = self.engine.pdf_data[slot]
                self.pdf_slots[slot] = d
                self.after(0, lambda: self._slot_loaded(slot, d))
            else:
                self.after(0, lambda: self._slot_error(slot, msg))

        self.engine.index_pdf(idx, path, done)

    def _slot_loaded(self, idx, data):
        slot_widget = self.sidebar.get_slot(idx)
        slot_widget.set_loaded(data['filename'], data['pages'], data['total_chunks'], data['size_kb'])
        self._update_count()
        self.chat_area.add_message(
            f"✅ PDF {idx+1} ready!\n"
            f"📄 {data['filename']}\n"
            f"📃 {data['pages']} pages → {data['total_chunks']} searchable chunks\n\n"
            f"You can now ask questions about this PDF!",
            "system"
        )
        self.mode_badge.configure(text="⬤  Ready", text_color=COLORS["accent_green"])

    def _slot_error(self, idx, msg):
        slot_widget = self.sidebar.get_slot(idx)
        slot_widget.set_error(msg)
        self.chat_area.add_message(f"❌ Slot {idx+1} load error:\n{msg}", "system")

    def _remove_pdf(self, idx: int):
        if self.pdf_slots[idx] is None:
            return
        fn = self.pdf_slots[idx]["filename"]
        self.pdf_slots[idx] = None
        self.engine.remove_pdf(idx)
        
        slot_widget = self.sidebar.get_slot(idx)
        slot_widget.set_empty()
        self._update_count()
        self.chat_area.add_message(f"🗑️ Removed {fn}.", "system")

    def _clear_all(self):
        for i in range(MAX_PDFS):
            self.pdf_slots[i] = None
            self.engine.remove_pdf(i)
            self.sidebar.get_slot(i).set_empty()
        self._update_count()
        self.chat_area.add_message("🗑️ All PDFs removed.", "system")

    def _update_count(self):
        n = sum(1 for s in self.pdf_slots if s is not None)
        self.sidebar.update_pdf_count(n)

    def _focus_in(self, placeholder):
        if self.q_input.get("0.0","end").strip() == placeholder:
            self.q_input.delete("0.0","end")
            self.q_input.configure(text_color=COLORS["text_primary"])

    def _focus_out(self, placeholder):
        if not self.q_input.get("0.0","end").strip():
            self.q_input.insert("0.0", placeholder)
            self.q_input.configure(text_color=COLORS["text_secondary"])

    def _send(self):
        if self.chat_area.is_thinking:
            return

        q = self.q_input.get("0.0","end").strip()
        placeholder = "Type your question here... (Hindi or English)"
        if not q or q == placeholder:
            self.q_input.configure(border_color=COLORS["accent_red"])
            self.after(600, lambda: self.q_input.configure(border_color=COLORS["border"]))
            return

        active = [i for i, s in enumerate(self.pdf_slots) if s is not None]
        if not active:
            messagebox.showinfo("No PDF", "Please load at least 1 PDF first!")
            return

        self.q_input.delete("0.0","end")
        self.chat_area.add_message(q, "user")

        self.send_btn.configure(state="disabled", text="⏳")
        self.mode_badge.configure(text="⬤  Thinking...", text_color=COLORS["accent_orange"])

        self.chat_area.show_thinking()

        def done(answer):
            self.after(0, lambda: self._finish(answer))

        self.engine.answer(q, active, done)

    def _finish(self, answer):
        self.chat_area.remove_thinking()
        self.chat_area.add_message(answer, "ai")
        self.send_btn.configure(state="normal", text="Send ➤")
        self.mode_badge.configure(text="⬤  Ready", text_color=COLORS["accent_green"])

    def _clear_chat(self):
        self.chat_area.clear()
        self._show_welcome()
