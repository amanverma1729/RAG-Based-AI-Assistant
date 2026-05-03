# 📄 PDF Intelligence Pro — 100% OFFLINE

> Koi API Key nahi • Koi Internet nahi • Tera data tera machine pe
> *Now featuring a modern Client-Server Architecture and a premium ChatGPT-Style Dark UI.*

---

## 🚀 Quick Start

The project is now split into two main components: a **FastAPI Backend** and a **React Frontend**.

### Step 1 — Install Backend Dependencies & Run Server
Open a terminal and navigate to the root directory:
```bash
pip install -r requirements_offline.txt
cd backend
uvicorn api:app --reload --port 8000
```
*(Pehli baar AI model download hoga — uske baad hamesha offline kaam karega!)*

### Step 2 — Install Frontend Dependencies & Run App
Open a second terminal and navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```
*(The React app will launch at `http://localhost:5173`)*

---

## 🏗️ Project Architecture

The application has been modularized into a robust client-server architecture for high scalability, separation of concerns, and easy maintenance:

```text
📁 / (Project Root)
├── 📁 backend/                 # FastAPI Python Backend (AI & Data)
│   ├── 📄 api.py               # Main REST API Endpoints
│   ├── 📁 config/              # Configuration (Settings, constants)
│   └── 📁 engine/              # Backend logic
│       ├── 📄 ai_engine.py     # Main AI orchestrator & Embeddings
│       ├── 📄 pdf_parser.py    # PDF text extraction and chunking
│       └── 📄 ollama_api.py    # Local LLM integration handling
│
├── 📁 frontend/                # React (Vite) Frontend (UI)
│   ├── 📄 package.json         # Node dependencies
│   ├── 📄 vite.config.js       # Vite configuration
│   └── 📁 src/
│       ├── 📄 App.jsx          # Main App state and routing
│       ├── 📄 index.css        # Premium ChatGPT-style dark theme & styles
│       └── 📁 components/      # Reusable React UI widgets
│           ├── 📄 Sidebar.jsx  # Responsive Sidebar with PDF slots
│           ├── 📄 ChatArea.jsx # Chat area, Markdown rendering & Copy button
│           ├── 📄 InputBar.jsx # User input and sending logic
│           └── 📄 TypeWriter.jsx # Real-time streaming text animation
│
├── 📄 requirements_offline.txt # Python backend dependencies
└── 📄 README_offline.md        # You are here
```

---

## 🧠 Kaise Kaam Karta Hai?

Yeh ek **RAG (Retrieval Augmented Generation)** system hai:

```text
[Frontend] Upload PDF -> API /upload
    ↓
[Backend] Text Extract (pdfplumber/pypdf)
    ↓
[Backend] Smart Chunks (400 words each, overlapping)
    ↓
[Backend] Sentence-Transformers se Embeddings (vectors)
    ↓
[Frontend] Ask Question -> API /chat
    ↓
[Backend] Sawaal bhi embed hota hai
    ↓
[Backend] Cosine Similarity → Top relevant chunks
    ↓
[Backend] Answer (Ollama LLM  OR  Smart Extraction)
    ↓
[Frontend] Typewriter Animation & Markdown Rendering
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
```

*The application will automatically detect if Ollama is running and use it!*

---

## ✨ Features

| Feature | Detail |
|---|---|
| **100% Offline** | Pehle model download ke baad internet nahi chahiye |
| **No API Key** | Bilkul free, koi subscription nahi |
| **Client-Server Architecture** | Clean, scalable React frontend + FastAPI backend |
| **5 PDFs** | Ek saath 5 PDFs load kar sakte ho |
| **Semantic Search** | Keyword nahi, meaning se dhundta hai |
| **Hindi + English** | Dono languages support |
| **Ollama Integration** | Local LLM se smart answers (optional) |
| **Premium ChatGPT UI** | Modern neutral dark mode, responsive sidebar, streaming typing animations, and copy-to-clipboard |

---

## 📋 Requirements

- **Python** 3.9+
- **Node.js** 18+ (for running the React frontend)
- **RAM** 4GB+ recommended
- **Disk** ~500MB (model cache ke liye)
- **Ollama** (optional, better answers ke liye)
