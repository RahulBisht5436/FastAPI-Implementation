# RAGAS Evaluation for personalChatBot

Production-grade RAG quality evaluation for the portfolio chatbot in `personalChatBot`.

## What this does

1. Calls the chatbot's secret-protected `POST /eval/run` endpoint for each golden question.
2. Collects `answer`, `contexts[]`, and metadata.
3. Runs official RAGAS metrics:
   - `faithfulness`
   - `answer_relevancy`
   - `context_precision`
   - `context_recall`
4. Writes JSON/Markdown reports and optionally compares against a baseline.

## Prerequisites

1. personalChatBot backend running with eval enabled:

```powershell
# In personalChatBot/.env
EVAL_MODE=true
EVAL_SECRET=change-me-to-a-long-random-secret
OPENAI_API_KEY=...
```

```powershell
cd C:\Users\rahul\OneDrive\Desktop\personalChatBot\streamingBackend
uv sync
uv run ingest-rag
$env:EVAL_MODE="true"
$env:EVAL_SECRET="change-me-to-a-long-random-secret"
uv run serve
```

2. RAGAS eval service configured:

```powershell
cd C:\Users\rahul\OneDrive\Documents\GitHub\FastAPI-Implementation\RAGAS
copy .env.example .env
uv sync
```

Use the same `EVAL_SECRET` in both `.env` files.

## Commands

```powershell
# Single question smoke test
uv run ragas-eval --question "What is your degree?"

# Full evaluation
uv run ragas-eval

# Smoke subset
uv run ragas-eval --max-samples 5

# Retrieval-only metrics
uv run ragas-eval --mode retrieval-only

# Save baseline after a stable run
uv run ragas-eval --update-baseline

# CI-style gate
uv run ragas-eval --fail-on-regression
```

Reports are written to `reports/<timestamp>/`.

## Golden dataset

- Path: `data/golden/v1.json`
- Tied to KB manifest hash `60afd3d85768e4508bc294dd96e1096b99b54f01ada3b31b37f3239afe8aceb4`
- Update the dataset when documents change and re-ingest the KB.

## Security

- Keep `EVAL_MODE=false` in production deployments.
- Eval routes require `X-Eval-Secret` and are localhost-only for `/eval/run`.
- Never commit real API keys.

## Project layout

```
RAGAS/
├── data/golden/v1.json
├── baselines/baseline-v1.json
├── src/ragas_eval/
│   ├── cli.py
│   ├── client/
│   ├── collector/
│   ├── dataset/
│   ├── metrics/
│   ├── report/
│   └── runner/
└── tests/
```
