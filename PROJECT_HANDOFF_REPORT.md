# College Environment / Local LLM Assistant — Project Handoff Report

**Prepared:** 2026-08-13  
**Repository:** `College_environment`  
**Current branch:** `updated_llm`  
**Purpose:** Give another LLM enough context to continue development without having to rediscover the project.

## 1. Executive summary

This repository is a minimal local AI college assistant. The intended product is a browser chat interface backed by a local Ollama language model, exposed through a FastAPI service. The application is deliberately small: there is currently no database, authentication, user accounts, conversation persistence, streaming, document retrieval/RAG, college knowledge base, admin panel, or deployment configuration.

The implemented path is:

`React/Vite browser UI` → `FastAPI /api/ai/chat` → `AIService` → `OllamaProvider` → `Ollama /api/chat` → local model response.

The UI also calls `GET /api/ai/status` to show whether the configured Ollama runtime and model are available. A basic backend health endpoint is available at `GET /api/health`.

The codebase is currently a working prototype skeleton rather than a complete college-specific assistant. The system prompt tells the model not to invent college facts, but no actual college data has been added yet.

## 2. What has been completed

- FastAPI application created with versioned settings and CORS middleware.
- Health endpoint implemented: `GET /api/health`.
- AI status endpoint implemented: `GET /api/ai/status`.
- Chat endpoint implemented: `POST /api/ai/chat` with `{ "message": "..." }`.
- Input trimming, empty-message validation, and maximum input-length validation implemented.
- Provider abstraction created so the backend is not hard-wired into route code.
- Ollama provider implemented using asynchronous HTTP requests.
- Ollama health check implemented using `/api/tags`.
- Non-streamed Ollama chat generation implemented using `/api/chat`.
- Provider failures are translated into safe API-facing errors instead of exposing raw exceptions.
- React/Vite single-page chat interface implemented.
- UI has message history for the current browser session, loading state, error display, disabled controls, and online/offline model status.
- Frontend API client and TypeScript response types implemented.
- Environment example and startup instructions documented in `README.md`.
- Local Python environment exists at `.venv/`; frontend dependencies exist locally in `frontend/node_modules/`.

## 3. Verification performed

The following checks were run during this audit:

- Backend Python bytecode compilation: **passed** (`compileall: OK`).
- Frontend production build: **passed** (`tsc -b && vite build`).
- Node.js available: `v22.22.2`.
- npm available: `10.9.7`.
- Python available in project virtual environment: `3.14.6`.
- Ollama connectivity check: **not available at audit time**; `http://localhost:11434` refused the connection.
- No automated backend tests were found in the repository.
- No live API integration test was completed because Ollama was not running.

The frontend build generated local build artifacts (`frontend/dist/` and TypeScript/Vite generated files). `frontend/dist/` is ignored by git, but the generated `frontend/tsconfig*.tsbuildinfo` and `frontend/vite.config.js/.d.ts` currently appear as untracked files and should be reviewed before committing.

## 4. File-by-file inventory

### Root files

#### `.env.example`

Template for local configuration. It defines the application name/version, debug mode, allowed frontend origins, provider name, Ollama URL/model, generation temperature, maximum output tokens, timeout, input limit, and default system prompt. It is not itself loaded as the active environment; a real `.env` file is expected and is ignored by git.

#### `.gitignore`

Excludes secrets/config (`.env`), the Python virtual environment, Python caches/bytecode, pytest/cache/coverage output, local database files under `data/`, frontend dependencies/build output, and log files.

#### `README.md`

Current operator documentation. It describes the project as a minimal Ollama-backed chat app, gives the Ollama model pull command, backend startup command, frontend startup command, browser URL, environment variables, and the three API routes. It does not yet document architecture, troubleshooting, tests, deployment, or college-specific functionality.

#### `PROJECT_HANDOFF_REPORT.md`

This document. It is the detailed continuation brief for another LLM or developer.

#### `backend/requirements.txt`

Python dependencies:

- `fastapi` — web framework/API routing.
- `uvicorn[standard]` — ASGI server.
- `pydantic-settings` — environment-backed typed settings.
- `pytest` — intended test framework, although tests are not present yet.
- `httpx` — asynchronous HTTP client used for Ollama calls and suitable for API testing.

### Backend package

#### `backend/app/__init__.py`

Package marker; no application logic.

#### `backend/app/main.py`

Creates the FastAPI application using settings for title and version. Adds permissive method/header CORS middleware restricted to configured origins, then mounts the health and AI routers under `/api`. This is the Uvicorn entry point: `app.main:app` with `--app-dir backend`.

#### `backend/app/config.py`

Defines the `Settings` class and cached `get_settings()` function. Settings are read from the project-root `.env` file when present, with defaults. The current defaults are:

- app name: `hazrat` (this is an uncommitted local change; the committed value was `AI College`)
- version: `0.1.0`
- provider: `ollama`
- Ollama URL: `http://localhost:11434`
- model: `qwen2.5:1.5b`
- temperature: `0.7`
- max output: `512` tokens
- timeout: `120` seconds
- max input: `8000` characters
- CORS: localhost ports 5173 and 5174, for both `localhost` and `127.0.0.1`

The current system prompt identifies the assistant as “AI College Assistant,” asks it not to invent college facts, and emphasizes very concise/fast responses. The prompt contains awkward wording and should be cleaned up when product behavior is finalized.

`cors_origin_list` converts the comma-separated CORS setting into a trimmed list.

#### `backend/app/api/__init__.py`

Package marker; no logic.

#### `backend/app/api/health.py`

Defines `GET /health` relative to the router. Because the router is mounted with `/api`, the public route is `GET /api/health`. Returns `status`, service name (`AI College Backend`), and configured application version.

#### `backend/app/api/ai.py`

Defines the AI router with `/ai` prefix, resulting in:

- `GET /api/ai/status`: asks the service/provider for runtime and model status.
- `POST /api/ai/chat`: validates the request, calls the provider, and returns a typed response.

Chat input is stripped before processing. Empty input returns HTTP 422. Input longer than `llm_max_input_characters` returns HTTP 422. Provider errors return HTTP 503. Successful responses contain `response`, `model`, and `provider`.

#### `backend/app/schemas/__init__.py`

Package marker; no logic.

#### `backend/app/schemas/ai.py`

Pydantic request/response models:

- `AIStatus`: provider, optional model, runtime, model availability, and status.
- `ChatRequest`: one string field named `message`, defaulting to an empty string.
- `ChatResponse`: generated response text, model name, and provider name.

#### `backend/app/services/__init__.py`

Package marker; no logic.

#### `backend/app/services/ai_service.py`

Application service layer. `AIService.status()` translates provider health data to `AIStatus`; `AIService.chat()` passes the user message and configured system prompt to the provider. The cached `get_ai_service()` selects `OllamaProvider` when `LLM_PROVIDER=ollama`; every other provider value gets `UnconfiguredProvider`. This means only Ollama is actually implemented.

#### `backend/app/services/llm/__init__.py`

Re-exports the provider abstraction, error types, Ollama implementation, and unconfigured fallback so callers can import them from `app.services.llm`.

#### `backend/app/services/llm/base.py`

Defines the provider contract and common types:

- `LLMProviderError`: safe base exception for provider failures.
- `LLMRuntimeUnavailable`: specific unavailable-runtime failure.
- `ProviderStatus`: immutable status data class containing runtime, model availability, and status.
- `LLMProvider`: abstract async `generate()` and `health_check()` methods.
- `UnconfiguredProvider`: safe fallback that reports `not_configured` and raises a clear error if used for chat.

#### `backend/app/services/llm/ollama_provider.py`

Ollama integration. It removes a trailing slash from the base URL and stores model, timeout, temperature, and token settings.

`health_check()` calls `GET {base_url}/api/tags`, handles HTTP/network/JSON failures as an offline result, and marks the model available only when an exact model name match is found.

`generate()` calls `POST {base_url}/api/chat` with a system message, user message, `stream: false`, temperature, and `num_predict`. It supports Ollama’s `message.content` response shape and falls back to a top-level `response` field. Connection, timeout, HTTP, malformed response, and empty response cases are converted into controlled provider errors.

### Frontend

#### `frontend/package.json`

Defines a private Vite React TypeScript app named `local-llm-assistant`, version `0.1.0`. Scripts are `dev`, `build` (`tsc -b && vite build`), and `preview`. React, React DOM, TypeScript, Vite, the React Vite plugin, and type packages are declared.

#### `frontend/package-lock.json`

npm lockfile pinning the resolved frontend dependency tree. Use `npm install` in `frontend/` when dependencies need to be restored.

#### `frontend/vite.config.ts`

Enables the React Vite plugin and configures the development server for port `5173`. There is no dev proxy; the frontend calls `http://localhost:8000/api` by default unless `VITE_API_URL` is supplied.

#### `frontend/index.html`

Minimal HTML shell with the page title `Local LLM Assistant`, viewport metadata, root element, and `src/main.tsx` module entry.

#### `frontend/src/main.tsx`

Creates the React root, renders `App` inside `StrictMode`, and imports global CSS.

#### `frontend/src/App.tsx`

The complete chat screen. It stores AI status, messages, input, loading, and error state in React hooks. On mount it requests AI status. On submit it trims input, prevents duplicate submissions, immediately appends the user message, calls the chat API, appends the assistant response, refreshes status, and shows errors when the request fails.

The rendered UI contains a header/status badge, chat transcript, empty state, “Thinking…” state, error text, offline hint, textarea, and send button. The textarea and button are disabled while the provider is offline or a request is in progress. The transcript uses `aria-live="polite"`.

Current limitation: messages exist only in React memory and disappear on refresh. The UI does not render markdown, citations, token counts, timestamps, retry controls, or streamed tokens.

#### `frontend/src/index.css`

Single-file dark visual design. It defines the page background, typography, header, teal online state, red/offline/error state, message cards, textarea, button, disabled button, spacing, and responsive width constraints. There is no component library or separate responsive breakpoint logic.

#### `frontend/src/services/api.ts`

Typed fetch wrapper. Base URL is `import.meta.env.VITE_API_URL` or `http://localhost:8000/api`. `request()` handles GET calls; `post()` handles JSON POST calls and extracts FastAPI’s `detail` on errors. Exposes `api.aiStatus()` and `api.chat(message)`.

#### `frontend/src/types/index.ts`

TypeScript interfaces matching backend payloads: `AIStatus` and `AIChatResponse`.

#### `frontend/src/vite-env.d.ts`

Vite-generated TypeScript environment declarations; currently not included in the earlier source dump because it contains only the standard Vite reference declaration.

#### `frontend/tsconfig.json`

Strict TypeScript compiler configuration targeting ES2020, browser libraries, bundler module resolution, React JSX transform, and source inclusion. It references the Node/Vite config project.

#### `frontend/tsconfig.node.json`

Composite TypeScript project configuration for `vite.config.ts`.

## 5. Runtime behavior and request contracts

### Startup

1. Install/start Ollama.
2. Pull the configured model, currently `qwen2.5:1.5b`.
3. Install backend dependencies into `.venv`.
4. Start Uvicorn on port 8000 with the backend directory as the app directory.
5. Install frontend dependencies and start Vite on port 5173.
6. Open `http://localhost:5173`.

### `GET /api/health`

Example response:

```json
{"status":"online","service":"AI College Backend","version":"0.1.0"}
```

This endpoint only proves that FastAPI is running. It does not prove Ollama is running.

### `GET /api/ai/status`

When Ollama is reachable and the exact model is installed, the expected shape is:

```json
{"provider":"ollama","model":"qwen2.5:1.5b","runtime":"available","model_available":true,"status":"online"}
```

If Ollama is unreachable, the provider reports `runtime: "unavailable"`, `model_available: false`, and `status: "offline"`. If Ollama is reachable but the configured model is absent, it reports an available runtime with `status: "error"`.

### `POST /api/ai/chat`

Request:

```json
{"message":"What can you help me with?"}
```

Successful response:

```json
{"response":"...","model":"qwen2.5:1.5b","provider":"ollama"}
```

The endpoint is non-streaming. The configured system prompt is sent on every request, but previous messages are not sent; each request is independent from the backend’s perspective.

## 6. Current repository state and caveats

There is one intentional-looking but uncommitted modification:

- `backend/app/config.py`: app name changed from `AI College` to `hazrat`; system prompt was extended with “Always answer concisely and fast”.

Do not discard this change without confirming its intended product name/prompt. There are also generated untracked files from the successful frontend build: `frontend/tsconfig.node.tsbuildinfo`, `frontend/tsconfig.tsbuildinfo`, `frontend/vite.config.d.ts`, and `frontend/vite.config.js`. They are build products rather than authored source and should either be ignored or removed after confirming they are not needed.

The current working branch is `updated_llm`. Recent commits indicate iterative prototype work, but the repository contains no task specification beyond the current README and source code. Therefore, product requirements below are inferred from the implemented app and naming, not from a formal requirements document.

## 7. Important gaps before calling this a full college assistant

1. **No college knowledge source:** There is no prospectus, timetable, faculty, department, fee, policy, FAQ, or campus data. The model cannot reliably answer college-specific questions.
2. **No retrieval/RAG:** Documents cannot be indexed, searched, cited, or updated.
3. **No conversation persistence:** Refreshing the page loses the transcript; the backend does not accept chat history.
4. **No authentication/authorization:** Anyone who can reach the API can use it.
5. **No abuse/rate controls:** There are input-size controls but no rate limiting, quotas, moderation, or request audit trail.
6. **No automated tests:** Route validation, provider error mapping, settings, and frontend behavior need tests.
7. **No live integration verification:** Ollama was offline during this audit.
8. **No production configuration:** No deployment files, reverse proxy, HTTPS, process manager, container setup, or production CORS policy.
9. **No streaming:** Responses wait for complete generation, so long answers feel less responsive.
10. **No frontend API configuration documentation:** `VITE_API_URL` is supported in code but absent from `.env.example` and README.
11. **Status semantics could be clearer:** `status: "error"` means the runtime is up but the model is unavailable; the frontend treats every non-`online` state simply as offline.
12. **Settings cache affects runtime edits:** `get_settings()` and `get_ai_service()` are cached, so changing environment variables requires a process restart.
13. **Prompt wording needs cleanup:** The current prompt contains grammar issues and potentially over-constrains all answers to very few lines.
14. **No explicit model name compatibility handling:** Ollama model tags may include variants/tags; exact matching can mark a usable model unavailable if configuration differs.

## 8. Recommended continuation order

### Phase A — make the prototype dependable

- Decide and commit the product name (`hazrat` versus `AI College`) and final system prompt.
- Start Ollama, pull the model, and manually verify health/status/chat.
- Add backend tests using `pytest` and mocked `httpx` responses.
- Add endpoint tests for empty input, over-limit input, provider unavailable, malformed provider output, and successful chat.
- Add `VITE_API_URL` to `.env.example` and README.
- Add generated TypeScript/Vite output patterns to `.gitignore` if they are not intended source.
- Improve frontend error text for runtime unavailable versus model missing.

### Phase B — make it a college assistant

- Gather authoritative college content and define ownership/update frequency.
- Add document ingestion and chunking.
- Add embeddings/vector search or another retrieval mechanism.
- Include retrieved context in prompts and require source citations.
- Add an explicit “I do not know” behavior when evidence is missing.
- Add tests for factual grounding and prompt-injection resistance from documents.

### Phase C — make it useful for real users

- Support conversation history and persistence.
- Add authentication and role-based access if student/staff data is involved.
- Add streaming responses, cancellation, retries, and request IDs.
- Add rate limiting, logging without sensitive content, metrics, and health/readiness separation.
- Add deployment configuration and secure production CORS/environment handling.

## 9. Handoff instructions for the next LLM

Treat this report and the source code as the current truth. Preserve the uncommitted `config.py` change unless the user decides otherwise. Before implementing college-specific answers, ask for or locate the authoritative college data; do not invent it. Keep Ollama behind the provider abstraction so another local/remote provider can be added without rewriting routes. Prefer small, testable changes and run backend compilation plus `npm run build` after frontend/backend edits. For live chat verification, ensure Ollama is running and the configured model is installed first.

The immediate next useful task is to add automated backend tests and resolve the product name/system-prompt decision, followed by adding the actual college knowledge source.
