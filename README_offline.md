# 📄 PDF Intelligence Pro — 100% OFFLINE

> Koi API Key nahi • Koi Internet nahi • Tera data tera machine pe
> *Now featuring a professional, modular architecture and a premium Dark UI.*

---

## 🚀 Quick Start

### Step 1 — Install Dependencies
```bash
pip install -r requirements_offline.txt
```

### Step 2 — Run the App
```bash
python -m src.main
```

**Pehli baar 80MB AI model download hoga — phir hamesha offline!**

---

## 🏗️ Project Architecture

The application has been modularized for scalability and easy maintenance:

```text
📁 / (Project Root)
├── 📁 src/                     # Source code root
│   ├── 📄 main.py              # Application entry point
│   ├── 📁 config/              # Configuration and styling
│   │   ├── 📄 settings.py      # App constants (CHUNK_SIZE, MAX_PDFS, etc.)
│   │   └── 📄 theme.py         # Premium color palettes and UI styling tokens
│   ├── 📁 engine/              # Backend logic (AI & Data)
│   │   ├── 📄 ai_engine.py     # Main AI orchestrator
│   │   ├── 📄 pdf_parser.py    # PDF text extraction and chunking
│   │   └── 📄 ollama_api.py    # Local LLM integration handling
│   ├── 📁 ui/                  # Frontend UI components
│   │   ├── 📄 app_window.py    # Main CustomTkinter window
│   │   └── 📁 components/      # Reusable UI widgets
│   │       ├── 📄 sidebar.py   # Sidebar with PDF slots and controls
│   │       ├── 📄 chat.py      # Chat area and message bubbles
│   │       └── 📄 pdf_slot.py  # PDF Slot UI component
├── 📄 requirements_offline.txt
└── 📄 README_offline.md
```

---

## 🧠 Kaise Kaam Karta Hai?

Yeh ek **RAG (Retrieval Augmented Generation)** system hai:

```text
PDF Upload
    ↓
Text Extract (pdfplumber/pypdf) -> src/engine/pdf_parser.py
    ↓
Smart Chunks (400 words each, overlapping)
    ↓
Sentence-Transformers se Embeddings (vectors) -> src/engine/ai_engine.py
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
python -m src.main
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| **100% Offline** | Pehle model download ke baad internet nahi chahiye |
| **No API Key** | Bilkul free, koi subscription nahi |
| **Modular Architecture** | Clean, scalable codebase split into config, engine, and ui modules |
| **5 PDFs** | Ek saath 5 PDFs load kar sakte ho |
| **Semantic Search** | Keyword nahi, meaning se dhundta hai |
| **Hindi + English** | Dono languages support |
| **Ollama Integration** | Local LLM se smart answers (optional) |
| **Premium UI** | CustomTkinter with deep dark mode colors and clean aesthetics |

---

## 📋 Requirements

- **Python** 3.9+
- **RAM** 4GB+ recommended
- **Disk** ~500MB (model cache ke liye)
- **Ollama** (optional, better answers ke liye)
