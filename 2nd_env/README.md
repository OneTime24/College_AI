# AI College Local

Local-first foundation for the AI College project. This first chunk builds the local LLM abstraction, a controlled agent, a deterministic tool registry, three simulated demo tools, and a small web UI that only talks to the backend API.

## What Is Built

- FastAPI backend with `/api/health`, `/api/system/status`, `/api/rooms`, `/api/rooms/{room_name}`, and `/api/agent/chat`
- Ollama provider abstraction using `LLM_PROVIDER`, `OLLAMA_BASE_URL`, and `OLLAMA_MODEL`
- Controlled agent loop with a small rule-based planner, optional LLM polishing, and a max tool-call guard
- Demo tools: `system_status`, `list_rooms`, `get_room_status`
- Simulated rooms only; no physical hardware control yet
- Static frontend served from the backend

## Current Environment

- OS: Linux Fedora
- CPU: Intel Core i7-10610U, 8 logical CPUs
- RAM: 15 GiB available at inspection time
- GPU: no NVIDIA GPU detected
- Python: 3.14.6
- Node: 22.22.2
- npm: 10.9.7
- Git: 2.55.0
- Ollama: installed and reachable, but no model was loaded at inspection time

## Run

Set up the environment variables you want, then start the backend:

```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:3b-instruct
python -m uvicorn backend.app.main:app --reload
```

If you want the bundled runner instead:

```bash
python -m backend.app.main
```

Open `http://127.0.0.1:8000` after the server starts.

## How It Works

The frontend sends a request to the backend API. The agent first tries a deterministic planner for known demo intents such as system status and room status. If the request is general and an LLM provider is configured, the agent uses Ollama for a concise response. Tool execution is always handled by registered tools only; shell commands are blocked.

## Simulated vs Functional

Functional now:

- Backend API
- Local LLM provider abstraction
- Agent routing and tool calling
- Conversation context for a short session window
- Demo web UI

Simulated now:

- Rooms and room status
- Device state inside demo room data
- All future hardware capabilities

## Next Chunk

Build the real room-control abstraction and simulator boundary, then add a proper IoT gateway layer before any camera or mirror work.
