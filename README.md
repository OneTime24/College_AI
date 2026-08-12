# AI College

AI College is a locally hosted assistant project. The only working user-facing feature for now is the local AI assistant, served on a separate public address, with a private dashboard gate on the other address.

## What works now

- Local Ollama-backed chat
- Separate public assistant address and private dashboard gate
- Typed input
- Human-like local spoken replies through `piper` when configured, with `espeak-ng` fallback
- Optional image attachments for vision-capable models

## Addresses

- Public assistant: `http://localhost:5174`
- Dashboard gate: `http://localhost:5173`

## Setup

1. Copy `.env.example` to `.env`.
2. Set `DASHBOARD_ACCESS_KEY` only if you want to protect the dashboard address.
3. For local voice input, set `WHISPER_CPP_BIN` to your whisper.cpp CLI binary and `WHISPER_CPP_MODEL` to a local Whisper model file.
4. For local voice replies, set `PIPER_TTS_BIN` to your Piper binary and `PIPER_TTS_MODEL` to a local voice `.onnx` file. Set `PIPER_TTS_CONFIG` if the model needs an explicit JSON config.
5. Run the backend from the project root:

```bash
.venv/bin/pip install -r backend/requirements.txt
cd backend
../.venv/bin/uvicorn app.main:app --reload --port 8000
```

4. Run the assistant frontend:

```bash
cd frontend
npm install
npm run dev:assistant
```

5. If you want the dashboard gate, run:

```bash
cd frontend
npm run dev:dashboard
```

## Voice flow

- Voice input uses whisper.cpp locally when `WHISPER_CPP_BIN` and `WHISPER_CPP_MODEL` are set.
- Replies use Piper locally when `PIPER_TTS_BIN` and `PIPER_TTS_MODEL` are set.
- `espeak-ng` is only a fallback for machines that do not have Piper configured.
- If the local speech engine is missing, the UI disables the button instead of failing.

## Image flow

- Attach an image from the composer.
- If the selected model supports vision, the image goes to the model.
- If not, the UI blocks submission and tells you why.

## API

- `GET /api/ai/status`
- `POST /api/ai/chat`
