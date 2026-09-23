# Portkey LLM Gateway

FastAPI service and learning notebook for routing LLM requests through [Portkey](https://portkey.ai).

## Setup

1. Copy environment template and add your keys locally:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Run the API:

   ```bash
   uv run fastapi dev src/portkey/main.py
   ```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PORTKEY_API_KEY` | Yes | Portkey API key from the dashboard |
| `PORTKEY_PROVIDER` | Yes | Provider slug from LLM Integrations (e.g. `@my-openai`) |
| `DEFAULT_LLM_MODEL` | No | Model name (default: `gpt-4o-mini`) |
| `OPENAI_API_KEY` | No | Used only for direct OpenAI calls in the notebook |
| `PORTKEY_RETRY_CONFIG_ID` | No | Dashboard retry config ID (`pc-...`) when inline configs are blocked |

**Security:** `.env` is gitignored. Do not commit API keys or paste them into source files or notebook outputs.

## Notebook

Open `portkeyNotebook.ipynb` for guided examples: direct OpenAI calls, Portkey gateway calls, metadata, and application-level retries.
