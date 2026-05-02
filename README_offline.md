# 📄 PDF Intelligence Pro — 100% OFFLINE

> Koi API Key nahi • Koi Internet nahi • Tera data tera machine pe

---

## 🚀 Quick Start

### Step 1 — Install karo
```bash
pip install -r requirements_offline.txt
```

### Step 2 — Run karo
```bash
python pdf_offline_qa.py
```

**Pehli baar 80MB AI model download hoga — phir hamesha offline!**

---

## 🧠 Kaise Kaam Karta Hai?

Yeh ek **RAG (Retrieval Augmented Generation)** system hai:

```
PDF Upload
    ↓
Text Extract (pdfplumber/pypdf)
    ↓
Smart Chunks (400 words each, overlapping)
    ↓
Sentence-Transformers se Embeddings (vectors)
    ↓
Sawaal poochho
    ↓
Sawaal bhi embed hota hai
    ↓
Cosine Similarity → Top relevant chunks
    ↓
Answer (Ollama LLM  OR  Smart Extraction)
```

---

## 🦙 Ollama se UPGRADE karo (Optional)

Ollama install karne se **full local LLM** se smart answers milenge:

```bash
# 1. Ollama install karo
# Windows/Mac/Linux: https://ollama.com/download

# 2. Model download karo (ek baar)
ollama pull llama3.2    # ~2GB — recommended
# ya
ollama pull mistral     # ~4GB — better quality
# ya
ollama pull phi3        # ~2GB — fast

# 3. Ollama chalao (background mein)
ollama serve

# 4. App open karo — automatically detect kar lega!
python pdf_offline_qa.py
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| **100% Offline** | Pehle model download ke baad internet nahi chahiye |
| **No API Key** | Bilkul free, koi subscription nahi |
| **5 PDFs** | Ek saath 5 PDFs load kar sakte ho |
| **Semantic Search** | Keyword nahi, meaning se dhundta hai |
| **Hindi + English** | Dono languages support |
| **Ollama Integration** | Local LLM se smart answers (optional) |
| **Dark Modern UI** | CustomTkinter se beautiful interface |

---

## 📋 Requirements

- **Python** 3.9+
- **RAM** 4GB+ recommended
- **Disk** ~500MB (model cache ke liye)
- **Ollama** (optional, better answers ke liye)
