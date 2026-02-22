# AI-Powered Parametric CAD Copilot

A fully local, zero-cost AI copilot that converts **natural language prompts** into **3D parametric models**. Type a description like *"Create an L-bracket with a 6mm mounting hole"* and get a rendered 3D solid in seconds — powered by a local LLM, FreeCAD, and a React + Three.js frontend.

---

## Architecture

```text
┌─────────────────────┐        ┌──────────────────────────┐        ┌───────────────────────┐
│   React Frontend    │        │    FastAPI Backend        │        │   FreeCAD (headless)  │
│  Vite + Tailwind 4  │──────▶│                          │──────▶│   FreeCADCmd.exe       │
│  Three.js 3D Viewer │◀──────│  ┌────────────────────┐  │◀──────│   Output: .STL files  │
│  Prompt + History   │ Proxy  │  │ Ollama LLM Service │  │ subprocess └───────────────────────┘
└─────────────────────┘ :5173  │  │ Code Validator     │  │ :8000
                               │  │ RAG (ChromaDB)     │  │
                               │  │ FreeCAD Executor   │  │
                               └──────────────────────────┘
                                         │
                                  ┌──────┴──────┐
                                  │   Ollama    │
                                  │  (Mistral)  │
                                  │   :11434    │
                                  └─────────────┘
```

## Features

- **100% Local** — No cloud APIs, no paid services. Everything runs on your machine.
- **Natural Language → 3D Model** — Describe a shape in plain English, get a rendered STL.
- **Complex Shapes** — Supports booleans (holes, cuts, fusions), extrusions, L-brackets, flanges, stepped shafts, bolt patterns, and more.
- **Interactive 3D Viewer** — Orbit, zoom, wireframe toggle via Three.js / React Three Fiber.
- **Refinement Loop** — Iteratively modify existing models with new instructions.
- **Secure Execution** — AST-based code validation blocks `os`, `sys`, `eval`, `exec` before any script reaches FreeCAD.
- **Prompt History** — LocalStorage-backed history with one-click replay.

---

## Prerequisites

Install these **before** starting setup:

| Tool | Version | Download |
|------|---------|----------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **FreeCAD** | 0.21+ or 1.0 | [freecad.org](https://www.freecad.org/downloads.php) |
| **Ollama** | Latest | [ollama.com](https://ollama.com/download) |
| **Git** | Any | [git-scm.com](https://git-scm.com/) |

> **Important**: After installing FreeCAD, note the full path to `FreeCADCmd.exe`. On a typical Windows install this is:
> `C:/Program Files/FreeCAD 1.0/bin/FreeCADCmd.exe`

---

## Step-by-Step Setup

### Step 1: Clone the Repository

```powershell
git clone https://github.com/your-username/3DModelAI.git
cd 3DModelAI
```

### Step 2: Install and Start Ollama

```powershell
# Download and install Ollama from https://ollama.com/download

# Pull the Mistral model (one-time, ~4.4 GB download)
ollama pull mistral

# Verify Ollama is running
ollama list
```

You should see `mistral:latest` in the output. Ollama runs as a background service on port `11434`.

### Step 3: Set Up the Backend

```powershell
# Navigate to backend directory
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install all Python dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create (or verify) the file `backend/.env` with the following content. **Use forward slashes** in the FreeCAD path:

```env
FREECAD_PATH="C:/Program Files/FreeCAD 1.0/bin/FreeCADCmd.exe"
LLM_MODEL="mistral"
OLLAMA_BASE_URL="http://127.0.0.1:11434"
```

> **Note**: If FreeCAD is installed in a different location, update `FREECAD_PATH` accordingly.

### Step 5: Set Up the Frontend

```powershell
# Open a NEW terminal and navigate to the frontend directory
cd frontend

# Install all Node.js dependencies
npm install
```

---

## Running the Application

You need **two terminal windows** running simultaneously.

### Terminal 1 — Start the Backend Server

```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:PYTHONDONTWRITEBYTECODE="1"
python main.py
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

### Terminal 2 — Start the Frontend Dev Server

```powershell
cd frontend
npm run dev
```

You should see:
```
VITE v7.x.x  ready in XXXms
➜  Local:   http://localhost:5173/
```

### Step 6: Open the Application

Open your browser and navigate to:

```
http://localhost:5173
```

✅ The **System Status** indicator (top-right) should show a **green checkmark**.

---

## Using the Application

### Basic Usage

1. Type a prompt describing the 3D model you want, e.g.:
   - `"Create a 30x30x30 mm box"`
   - `"Create a cylinder with radius 15 and height 40"`

2. Press **Ctrl + Enter** or click the blue send button.

3. Wait 30–90 seconds (depends on your hardware — the local LLM needs time to generate code).

4. The 3D model renders in the interactive viewer on the right.

### Complex Shapes

The system handles multi-body parametric models with boolean operations:

| Prompt | What It Creates |
|--------|----------------|
| `"Create an L-bracket: vertical arm 10x40x60mm, horizontal arm 50x40x10mm"` | Two rectangular arms fused at a right angle |
| `"Create a 50mm cube with a 10mm diameter hole through the center"` | Box with cylindrical cutout |
| `"Create a hollow cylinder: outer radius 20mm, inner radius 15mm, height 50mm"` | Pipe/tube shape |
| `"Create a plate 100x60x5mm with 4 bolt holes of 8mm diameter in the corners"` | Flat plate with 4 cylindrical cutouts |
| `"Create a cone frustum with bottom radius 30mm, top radius 15mm, height 50mm"` | Truncated cone |
| `"Create a flanged shaft: shaft radius 10mm length 80mm, flange radius 25mm thickness 8mm"` | Shaft with wider disk at base |

### Refinement

1. Check the **"Refine existing model"** checkbox.
2. Type a modification instruction, e.g.: `"Add 4 bolt holes to the base plate"`.
3. Submit. The LLM uses the previous code as context to make targeted changes.

### Code Inspection

Click **"View Code"** at the bottom to see the generated FreeCAD Python script. You can also copy or download it.

---

## Project Structure

```
3DModelAI/
├── frontend/                      # React SPA
│   ├── src/
│   │   ├── App.jsx                # Main app: state management, API calls
│   │   ├── components/
│   │   │   ├── TopNav.jsx         # Header bar with system status indicator
│   │   │   ├── PromptInput.jsx    # Text input with refinement toggle
│   │   │   ├── Viewer3D.jsx       # Three.js canvas for STL rendering
│   │   │   ├── CodePreview.jsx    # Slide-out code viewer panel
│   │   │   └── HistoryPanel.jsx   # Prompt history (localStorage)
│   │   └── index.css              # Global styles + Tailwind
│   ├── vite.config.js             # Vite config with /api and /outputs proxy
│   └── package.json
│
├── backend/                       # FastAPI application
│   ├── main.py                    # Entry point, CORS, static files, Uvicorn
│   ├── .env                       # Environment variables (FreeCAD path, LLM model)
│   ├── requirements.txt           # Python dependencies
│   ├── api/
│   │   ├── routes.py              # /generate, /refine, /status endpoints + system prompt
│   │   └── models.py              # Pydantic request/response schemas
│   ├── services/
│   │   ├── llm.py                 # Ollama HTTP client with retry and code extraction
│   │   ├── executor.py            # FreeCAD headless subprocess runner
│   │   ├── validator.py           # AST-based security scanner
│   │   └── rag.py                 # ChromaDB vector search for context injection
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (.env loader)
│   │   ├── logger.py              # Structured logging
│   │   └── errors.py              # Custom exceptions + FastAPI error handlers
│   ├── outputs/                   # Generated .py scripts and .stl files
│   ├── rag_docs/                  # Markdown docs for RAG knowledge base
│   └── chroma_db/                 # ChromaDB persistence directory
│
├── setup.ps1                      # Automated Windows setup script
└── README.md
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React, Vite, Tailwind CSS 4 | SPA with dark-mode UI |
| **3D Rendering** | Three.js, React Three Fiber, Drei | Interactive STL viewer |
| **Backend** | FastAPI, Uvicorn, Pydantic | REST API server |
| **LLM** | Ollama + Mistral 7B | Local code generation from prompts |
| **CAD Engine** | FreeCAD (headless) | BRep solid geometry + STL export |
| **Knowledge Base** | ChromaDB, Sentence-Transformers | RAG context retrieval |
| **Security** | Python AST module | Code validation before execution |

---

## Configuration Reference

All settings are configured via `backend/.env`. Defaults are used if not specified.

| Variable | Default | Description |
|----------|---------|-------------|
| `FREECAD_PATH` | *(none — required)* | Absolute path to `FreeCADCmd.exe` |
| `LLM_MODEL` | `mistral` | Ollama model name |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API endpoint |
| `API_HOST` | `127.0.0.1` | Backend bind address |
| `API_PORT` | `8000` | Backend port |
| `LLM_TIMEOUT` | `180` | LLM request timeout (seconds) |
| `FREECAD_TIMEOUT` | `30` | FreeCAD execution timeout (seconds) |
| `ENABLE_RAG` | `true` | Enable/disable RAG context injection |
| `MAX_SCRIPT_LENGTH` | `2000` | Max allowed lines in generated script |
| `LOG_LEVEL` | `INFO` | Python logging level |

---

## Troubleshooting

### "Failed to fetch" or CORS Error
- Ensure the backend is running on `127.0.0.1:8000` (not `0.0.0.0`)
- Ensure the frontend is running on `localhost:5173`
- The Vite proxy in `vite.config.js` routes `/api` and `/outputs` to the backend — no direct cross-origin calls needed

### System Status Shows Red ✖
- **Ollama not reachable**: Run `ollama list` to verify it's running. Pull a model with `ollama pull mistral`.
- **FreeCAD not found**: Verify `FREECAD_PATH` in `.env` uses forward slashes and points to `FreeCADCmd.exe`.

### Generation Takes Too Long
- The Mistral 7B model runs on CPU by default. Generation can take 30–120 seconds.
- If you have a GPU, Ollama automatically uses it when available (NVIDIA CUDA or Apple Metal).
- Alternatively, use a smaller model: set `LLM_MODEL="gemma3:1b"` in `.env` for faster (but less capable) generation.

### "NotImplementedError" in Backend Logs
- This is a Windows asyncio bug. The backend already includes the fix (`asyncio.to_thread` + `WindowsProactorEventLoopPolicy`). If you see this, restart the backend with: `$env:PYTHONDONTWRITEBYTECODE="1"` before `python main.py`.

### Server Restarts During Generation
- The Uvicorn file watcher may detect generated `.py` files in `outputs/`. The `reload_excludes` setting in `main.py` prevents this. If it still happens, restart the backend.

---

## Security

The backend validates **every** LLM-generated script before executing it:

1. **AST Parsing** — The code is parsed into an Abstract Syntax Tree. Any syntax error is rejected.
2. **Banned Imports** — `os`, `sys`, `subprocess`, `socket`, `urllib`, `requests`, `http`, `threading`, `multiprocessing` are blocked.
3. **Banned Functions** — `exec()`, `eval()`, `open()`, `compile()`, `__import__()`, `getattr()` are blocked.
4. **Length Limits** — Scripts exceeding 2000 lines are rejected.
5. **Execution Sandbox** — FreeCAD runs as a subprocess with a 30-second timeout. The process is killed if it exceeds the limit.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/status` | Health check — returns Ollama, FreeCAD, and RAG status |
| `POST` | `/api/generate` | Generate a 3D model from a natural language prompt |
| `POST` | `/api/refine` | Modify an existing model with a new instruction |

### Example API Call

```bash
curl -X POST http://127.0.0.1:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a 20x20x20 mm box"}'
```

Response:
```json
{
  "status": "success",
  "stl_url": "/outputs/uuid-here.stl",
  "code": "import FreeCAD\nimport Part\nfinal_shape = Part.makeBox(20, 20, 20)"
}
```

---

## License

This project is for educational and research purposes. FreeCAD is licensed under LGPL. Ollama and Mistral have their own respective licenses.
