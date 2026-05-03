import os
import re
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import TOP_K_CHUNKS
from engine.pdf_parser import extract_text, make_chunks
from engine.ollama_api import check_ollama, query_ollama

class OfflineAIEngine:
    def __init__(self):
        self.model      = None          # sentence-transformers model
        self.pdf_data   = {}            # slot_index -> {chunks, embeddings, meta}
        self.model_name = "all-MiniLM-L6-v2"
        self.ollama_model = None        # detected ollama model name

    def load_model(self):
        """Synchronously load the sentence-transformer model."""
        if self.model is not None:
            return True, "Model already loaded"

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            return True, "Model ready!"
        except Exception as e:
            return False, str(e)

    def index_pdf(self, slot_index: int, pdf_path: str):
        """Synchronously extract text, chunk, and embed."""
        try:
            # 1. Extract text
            text, pages = extract_text(pdf_path)

            # 2. Split into chunks
            chunks = make_chunks(text)

            # 3. Create embeddings
            if self.model is None:
                return False, "AI Model not loaded yet!"

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
            return True, {"filename": Path(pdf_path).name, "pages": pages, "total_chunks": len(chunks), "size_kb": self.pdf_data[slot_index]["size_kb"]}
        except Exception as e:
            return False, str(e)

    def answer(self, question: str, active_slots: list[int]):
        """Synchronously find answer to the question."""
        try:
            if self.model is None:
                return "❌ AI model not loaded. Please wait."

            q_embedding = self.model.encode([question])[0]

            all_chunks = []
            for slot in active_slots:
                if str(slot) in self.pdf_data:
                    slot_key = str(slot)
                elif int(slot) in self.pdf_data:
                    slot_key = int(slot)
                else:
                    continue
                    
                data = self.pdf_data[slot_key]
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
                return "🔍 No relevant answer found in the loaded PDFs.\n\nTry rephrasing or load different PDFs."

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
                    return ollama_ans

            # Fallback to Smart extractive answer
            ans = self._build_extractive_answer(question, top_chunks)
            return ans

        except Exception as e:
            return f"❌ Error: {str(e)}"

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
        if str(slot_index) in self.pdf_data:
            self.pdf_data.pop(str(slot_index), None)
        if int(slot_index) in self.pdf_data:
            self.pdf_data.pop(int(slot_index), None)
