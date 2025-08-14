# AI Career Coach Backend

Requirements:
- Python 3.13 with venv
- OpenAI API key
- Tavily API key (optional but recommended)

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

Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `TAVILY_API_KEY`.

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
- POST `/api/chat`
- GET `/api/chat/stream?session_id=...&message=...`
- POST `/api/user`
- GET `/api/user/{session_id}`