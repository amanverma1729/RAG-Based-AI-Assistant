import threading
import os
import re
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.config.settings import TOP_K_CHUNKS
from src.engine.pdf_parser import extract_text, make_chunks
from src.engine.ollama_api import check_ollama, query_ollama

class OfflineAIEngine:
    def __init__(self, status_callback=None):
        self.status_cb  = status_callback or (lambda msg, color: None)
        self.model      = None          # sentence-transformers model
        self.pdf_data   = {}            # slot_index -> {chunks, embeddings, meta}
        self.model_name = "all-MiniLM-L6-v2"
        self._model_loading = False
        self.ollama_model = None        # detected ollama model name

    def load_model(self, done_callback):
        """Background load of sentence-transformer model."""
        if self.model is not None:
            done_callback(True, "Model already loaded")
            return
        self._model_loading = True

        def worker():
            try:
                self.status_cb("🔄 Downloading/Loading AI Model (80MB, first time only)...", "orange")
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                self._model_loading = False
                done_callback(True, "Model ready!")
            except Exception as e:
                self._model_loading = False
                done_callback(False, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def index_pdf(self, slot_index: int, pdf_path: str, done_callback):
        """PDF load + chunk + embed in background."""
        def worker():
            try:
                # 1. Extract text
                text, pages = extract_text(pdf_path)

                # 2. Split into chunks
                chunks = make_chunks(text)

                # 3. Create embeddings
                if self.model is None:
                    done_callback(False, slot_index, "AI Model not loaded yet!")
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
        """Find answer to the question in background."""
        def worker():
            try:
                if self.model is None:
                    done_callback("❌ AI model not loaded. Please wait.")
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
                    done_callback("🔍 No relevant answer found in the loaded PDFs.\n\nTry rephrasing or load different PDFs.")
                    return

                all_chunks.sort(key=lambda x: x["score"], reverse=True)
                top_chunks = all_chunks[:TOP_K_CHUNKS]

                # Try Ollama first
                if not self.ollama_model:
                    ok, name = check_ollama()
                    if ok and "No models" not in name:
                        self.ollama_model = name

                if self.ollama_model:
                    ollama_ans = query_ollama(self.ollama_model, question, top_chunks)
                    if ollama_ans:
                        done_callback(ollama_ans)
                        return

                # Fallback to Smart extractive answer
                ans = self._build_extractive_answer(question, top_chunks)
                done_callback(ans)

            except Exception as e:
                done_callback(f"❌ Error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

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

            highlighted = self._highlight_keywords(text, question)

            lines.append(f"━━ 📄 {fname}  |  Page {page}  |  Relevance: {int(score*100)}%")
            lines.append(f"{highlighted}\n")

        lines.append(f"\n💡 **Tip:** Install **Ollama** for better answers (ollama.com)")
        lines.append(f"   Run: `ollama pull llama3.2` — runs AI locally! 🚀")

        return "\n".join(lines)

    def _highlight_keywords(self, text: str, question: str) -> str:
        stop = {"kya","hai","ka","ke","ki","mein","se","ko","tha","the","hain",
                "what","is","the","a","an","of","in","to","for","and","or","how",
                "when","where","who","which","tell","me","about","please"}
        words = [w.lower().strip("?.,!") for w in question.split() if w.lower() not in stop and len(w) > 2]

        result = text
        for word in words[:5]:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result  = pattern.sub(f"»{word}«", result, count=3)
        return result

    def remove_pdf(self, slot_index: int):
        self.pdf_data.pop(slot_index, None)
