# Local LLM Assistant

A minimal Ollama-backed chat app. It contains only the LLM API and one-page chat frontend.

## Run

Install Ollama, then pull the configured model (defaults to `qwen2.5:1.5b`):

```bash
ollama pull qwen2.5:1.5b
./.venv/bin/pip install -r backend/requirements.txt
./.venv/bin/uvicorn app.main:app --app-dir backend --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Set `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, or `LLM_SYSTEM_PROMPT` in `.env` when needed.

## API

- `GET /api/health`
- `GET /api/ai/status`
- `POST /api/ai/chat` with `{ "message": "..." }`
