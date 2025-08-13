# AI Career Coach Backend

Requirements:
- Python 3.13 with venv
- OpenRouter API key for Grok-3 (preferred) or xAI/OpenAI API key as fallback
- Tavily API key (optional)

Setup

1. Create and activate venv

```
python3 -m venv /workspace/.venv
source /workspace/.venv/bin/activate
```

2. Install dependencies

```
pip install -U pip wheel setuptools
pip install -r backend/requirements.txt
```

3. Configure environment

Copy `.env.example` to `.env` and set one of:
- `OPENROUTER_API_KEY` (uses `MODEL_NAME=x-ai/grok-3` via `OPENROUTER_BASE_URL`)
- or `XAI_API_KEY` (uses Grok via `XAI_BASE_URL`)
- or `OPENAI_API_KEY` (fallback)

```
cp backend/.env.example backend/.env
```

4. Ingest datasets

- Put CSVs from Kaggle datasets into `backend/data/raw/` (auto-download if Kaggle CLI is configured).
- Run:

```
python backend/ingest.py
```

5. Run server

```
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

API
- POST `/api/chat` (streams also available at `/api/chat/stream`)
- POST `/api/user`
- GET `/api/user/{session_id}`