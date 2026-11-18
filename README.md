# Crew Execution Runner 🤖

![CI](https://github.com/rawfu-siam/crew-execution-runner/actions/workflows/ci.yml/badge.svg)

> Autonomous B2B Lead Research & Slack Operations Crew

Crew Execution Runner is a FastAPI backend that runs a multi-agent CrewAI crew to research a target company, find operational bottlenecks, and draft a custom AI automation proposal. Every crew output is validated with Pydantic before it is stored, successful runs are pushed to n8n for CRM automation, and any crash is caught and reported to Slack as a rich diagnostic card.

---

## 🎯 The Problem

Boutique AI automation agencies want to scale client prospecting with autonomous research, but production AI pipelines fail quietly: LLM output comes back malformed, third-party APIs hit rate limits, and a dead script goes unnoticed while leads pile up. Crew Execution Runner is built so that output is schema-checked before it touches the database, failures are recorded instead of lost, and the team hears about every crash in Slack within seconds.

---

## ✨ Features

- **Two-agent CrewAI crew**: a Senior B2B Technical Auditor & Lead Researcher finds bottlenecks, then a Principal AI Solutions Architect turns the findings into a proposal with a confidence score
- **Strict output validation**: the crew must return JSON matching a Pydantic schema (confidence score bounded between 0.0 and 1.0), and anything else is rejected instead of saved
- **Non-blocking API**: the crew runs in a thread pool as a background task, so the API answers immediately with `202 Accepted`
- **Lead lifecycle tracking**: every request is stored in SQLite/SQLAlchemy and moves through `PROCESSING` → `COMPLETED` or `FAILED`
- **n8n webhook dispatch**: completed leads are posted to an n8n webhook as a structured JSON payload for CRM and Notion automation
- **Slack failure alerts**: a global exception handler turns Python tracebacks into Slack Block Kit cards with error details and request context
- **Safe when unconfigured**: placeholder Slack or n8n URLs are detected and skipped with a warning, and every dispatch failure is logged without crashing the app
- **Startup validation**: required environment variables are checked when the app boots, so a missing key fails fast
- **Rotating logs**: logging to console and a rotating `app.log` (50 KB per file, 3 backups)
- **Health endpoint** for container and uptime probes

---

## 🔄 How It Works

```text
POST /api/v1/leads/research
        │
        ▼
 Save lead (PROCESSING) ──► return 202 + lead record
        │
        ▼  (background task)
 CrewAI crew: Auditor ──► Solutions Architect
        │
        ▼
 Pydantic validation of crew output
        │
   ┌────┴─────────────┐
   ▼                  ▼
 success            failure
 lead = COMPLETED   lead = FAILED
 POST to n8n        Slack Block Kit alert
```

Poll `GET /api/v1/leads/{id}` to see the final status and analysis.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI, Uvicorn |
| Multi-agent AI | CrewAI, OpenAI API |
| Database & ORM | SQLite via SQLAlchemy 2.x (swappable through `DATABASE_URL` with the matching driver) |
| Config & validation | Pydantic v2, pydantic-settings |
| Outbound HTTP | httpx (async) |
| Integrations | Slack Block Kit incoming webhooks, n8n webhooks |
| Code quality | Ruff (lint + format), Bandit (security scan), pre-commit |
| Testing | pytest, pytest-asyncio |
| DevOps | Docker, Docker Compose, GitHub Actions |

---

## 📂 Project Structure

```text
crew-execution-runner/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions: Ruff, Bandit, pytest
├── config/
│   ├── __init__.py
│   └── settings.py                # Pydantic settings and env validation
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, lifespan, and endpoints
│   ├── crew/
│   │   ├── __init__.py
│   │   ├── agents.py              # CrewAI agent definitions
│   │   ├── tasks.py               # CrewAI tasks with strict output schema
│   │   └── management.py          # Crew orchestration, DB updates, dispatch
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # SQLAlchemy engine and session dependency
│   │   └── models.py              # LeadRecord ORM model
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── exception_handler.py   # Traceback to Slack alert interceptor
│   │   ├── slack_client.py        # Async Slack webhook client
│   │   └── n8n_dispatcher.py      # Async n8n webhook dispatcher
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── lead_validation.py     # Pydantic request, crew output, response models
│   │   └── slack_blocks.py        # Slack Block Kit payload builders
│   └── utils/
│       ├── __init__.py
│       └── logger.py              # Dual-stream rotating logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # In-memory DB, test client, safe test env
│   ├── test_crew_flows.py         # API endpoint tests with mocked crew
│   └── test_operations_hub.py     # Slack, n8n, and exception handler tests
├── .dockerignore
├── .env.example                   # Environment variable template
├── .gitignore
├── .pre-commit-config.yaml        # Ruff and Bandit hooks before every commit
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Option A: Local

```bash
git clone https://github.com/rawfu-siam/crew-execution-runner.git
cd crew-execution-runner
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit the values
uvicorn src.main:app --reload
```

Open **http://localhost:8000/docs** to test every endpoint in Swagger UI.

### Option B: Docker

```bash
cp .env.example .env             # then edit the values
docker compose up --build
```

The API is served on port 8000. The SQLite database and logs are stored in named Docker volumes (`crew_data` and `crew_logs`), so they survive container restarts. Run `docker compose down -v` to wipe them.

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and set:

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | none | OpenAI API key used by the CrewAI agents |
| `SLACK_WEBHOOK_URL` | Yes | none | Slack incoming webhook for the `#alerts` channel |
| `N8N_WEBHOOK_URL` | Yes | none | n8n webhook that receives completed lead payloads |
| `DATABASE_URL` | No | `sqlite:///./crew_runner.db` | SQLAlchemy connection URL |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

The app refuses to start if a required variable is missing. If the Slack or n8n URL is left at its `.env.example` placeholder value, that integration is skipped with a warning instead of failing. `.env` is git-ignored and excluded from Docker images, and only `.env.example` is committed.

Each research request makes real OpenAI API calls, which cost money, so watch your usage.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service liveness check, used by the Docker healthcheck |
| `POST` | `/api/v1/leads/research` | Create a lead record and start the research crew in the background (`202 Accepted`) |
| `GET` | `/api/v1/leads/{lead_id}` | Fetch a lead record and its current status (`404` if the ID does not exist) |

**Example request**

```bash
curl -X POST http://localhost:8000/api/v1/leads/research \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Acme Corp", "target_url": "https://acme.example.com"}'
```

**Example response (immediately)**

```json
{
  "id": 1,
  "company_name": "Acme Corp",
  "target_url": "https://acme.example.com/",
  "status": "PROCESSING",
  "bottlenecks": null,
  "proposed_solution": null,
  "confidence_score": null
}
```

Once the crew finishes, `GET /api/v1/leads/1` returns the same record with `status` set to `COMPLETED` and the `bottlenecks`, `proposed_solution`, and `confidence_score` fields filled in. If the crew fails, the status becomes `FAILED` and a diagnostic card is sent to Slack.

**n8n payload** sent on success:

```json
{
  "id": 1,
  "company_name": "Acme Corp",
  "target_url": "https://acme.example.com/",
  "status": "COMPLETED",
  "bottlenecks": "...",
  "proposed_solution": "...",
  "confidence_score": 0.82
}
```

An invalid request body (empty company name or malformed URL) is rejected with `422` before anything is saved.

---

## 🧪 Testing & Code Quality

```bash
pytest -v                          # run the test suite
ruff check .                       # lint
ruff format --check .              # formatting check
bandit -c pyproject.toml -r src/   # security scan
```

The tests use an in-memory SQLite database, dummy environment variables, and a mocked crew and mocked webhooks, so they never call OpenAI, Slack, or n8n.

Enable the pre-commit hooks so Ruff and Bandit run automatically before every commit:

```bash
pre-commit install
```

On every push and pull request to `main`, `master`, or `develop`, GitHub Actions installs the dependencies, runs Ruff and Bandit, and executes the full pytest suite.

---

## ⚠️ Known Limitations

- The agents have no web-scraping tool yet, so the website audit relies on the model's general knowledge of the target company. Scraped page content (for example from Playwright) is the next planned improvement.
- SQLite is single-writer, so the Docker image runs one Uvicorn worker. Point `DATABASE_URL` at PostgreSQL before scaling out.
- Crew runs are background tasks inside the API process, so a run in progress is lost if the container restarts.

---

## 🤝 Responsible Use

Generated research and proposals come from an AI model and can contain mistakes. Review them before sending anything to a prospect, and only research companies and contact people in line with applicable privacy and outreach laws.

---

## 👤 Author

**Rawfu Siam**: [github.com/rawfu-siam](https://github.com/rawfu-siam)
