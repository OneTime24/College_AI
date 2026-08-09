# AI College Architecture

## Current foundation

```
React + TypeScript dashboard
           ↓ HTTP / JSON
        FastAPI API
           ↓
   Application services
           ↓
        SQLAlchemy
           ↓
          SQLite
```

The frontend reads dashboard status, rooms, devices, and events from FastAPI. The API delegates database work to room, device, and event services. SQLite stores local demonstration records at `data/ai_college.db`.

Demo records are initialized once and visibly labelled as simulations; physical hardware is not claimed to be connected.

## Local AI engine

```
AI College frontend
           ↓ HTTP / JSON
        FastAPI
           ↓
       AI Service
           ↓
   LLM Provider interface
           ↓
      Ollama provider
           ↓
      Ollama runtime
           ↓
       Local model
```

The API routes do not contain model-specific logic. They depend on `AIService`, which delegates generation and health checks to an `LLMProvider` interface. The initial implementation is `OllamaProvider`; a future laptop or college-server provider/model can be substituted at the service boundary with minimal application changes. Runtime URL, model, generation settings, timeout, and system prompt are environment configuration rather than frontend or route constants.

`GET /api/ai/status` independently checks the runtime and configured model. `POST /api/ai/chat` uses normal request/response generation. An unavailable runtime remains contained to the AI service, so the dashboard and rest of the backend remain usable.

## Future integration

Future local components will connect through backend services: RAG knowledge base, vision services, IoT adapters, Kudos robot integration, and a secured centralized college network. These are intentionally not implemented in this phase.
