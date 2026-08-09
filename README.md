<<<<<<< HEAD
This repo will have all the files to automate and integrate ai in college
=======
# AI College

AI College is a centralized, locally hosted intelligent college infrastructure. It includes a working dashboard, SQLite-backed foundation, and a fully local AI integration through Ollama.

## Current

- FastAPI, SQLAlchemy, SQLite, CORS, environment configuration, logging, and Swagger docs.
- Demo seed data: six rooms, eleven simulated devices, and activity events.
- React + TypeScript dashboard that loads all displayed data from the live backend API.
- CRUD API for rooms and devices; read/create API for events.
- A provider-based AI service that talks to a local Ollama model only; no cloud AI API is used.
- AI Assistant chat UI with live local-runtime status and graceful offline handling.
- Pytest coverage for AI status, validation, provider offline behavior, and mocked chat behavior.

Demo infrastructure records are explicitly simulation data. The AI assistant is a general-purpose local assistant and does not claim unprovided college facts.

## Future

College RAG, vision, people counting, IoT adapters, Kudos, authentication, and centralized administration will be developed later.

## Architecture

`React frontend → FastAPI → application services → SQLAlchemy → SQLite`

`React frontend → FastAPI → AI Service → LLM Provider → Ollama → local model`

See [architecture.md](docs/architecture.md).

## Local AI setup

The development default is `qwen2.5:1.5b`, a lightweight ~1.5B-parameter instruct model suitable for a CPU laptop with 16 GB RAM. It is a development model only; deploy a stronger local model on the college server by changing environment variables, without application code changes.

1. Install Ollama with the official Linux instructions at [ollama.com/download/linux](https://ollama.com/download/linux). The usual command is `curl -fsSL https://ollama.com/install.sh | sh`.
2. Check the runtime: `ollama --version` and `ollama list`.
3. Pull the development model: `ollama pull qwen2.5:1.5b`.
4. Start the runtime if it is not already managed by your system: `ollama serve`.
5. Copy `.env.example` to `.env` and set `LLM_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, and `LLM_TIMEOUT` as appropriate.

The backend never downloads models and never forwards prompts to any cloud service. Ollama owns local model downloads and execution.

## Run

Optionally copy configuration:

```bash
cp .env.example .env
```

Backend (from the project root):

```bash
.venv/bin/pip install -r backend/requirements.txt
cd backend
../.venv/bin/uvicorn app.main:app --reload --port 8000
```

Database initialization is automatic. API docs: http://localhost:8000/docs

Frontend (new terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The default API target is `http://localhost:8000/api`; set `VITE_API_URL` to override it.

Open **AI Assistant** in the sidebar. The status indicator will show LOCAL AI ONLINE only when both Ollama and the configured model are available.

## Tests

```bash
cd backend
../.venv/bin/python -m pytest
```

Tests cover health, database initialization, core APIs, AI status, empty-message rejection, mocked chat success, and unavailable Ollama runtime handling. They do not require a running local model.

## API

- `GET /api/health`
- `GET /api/system/status`
- `GET /api/ai/status`
- `POST /api/ai/chat` with `{ "message": "..." }`
- CRUD `/api/rooms`
- CRUD `/api/devices`
- `GET` and `POST /api/events` (filters: `limit`, `location`, `event_type`)
>>>>>>> ec5e480 (llm version 2)
