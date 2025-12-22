# Stampli Churn Risk Analyzer - AI Context

## Project Overview
A multi-agent system that analyzes Gong call transcripts to assess customer churn risk for Stampli (an AP automation SaaS). Built with **LangGraph + LangChain + FastAPI** microservices, deployed via **Docker Compose**.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend UI    │────▶│  Manager Agent   │────▶│ Transcript      │
│  (FastAPI+HTML) │     │  (Orchestrator)  │     │ Retriever       │
│  Port 8000      │     │  Port 8080       │     │ Port 8001       │
└─────────────────┘     └────────┬─────────┘     └────────┬────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌────────────────┐       ┌────────────────┐
                        │ Churn Analyzer │       │ Gong Database  │
                        │ Port 8002      │       │ REST API       │
                        └────────────────┘       └────────────────┘
```

## Key Components

### 1. Manager Agent (`agents/manager.py`)
- **Role**: Orchestrates workflow using LangGraph StateGraph
- **Flow**: Extract intent → Retrieve transcripts → (Optional) Analyze → Format output
- **Smart defaults**: 
  - Analysis requests: 2 transcripts (faster LLM)
  - Transcript requests: 5 transcripts (more data)
- **Models used**: `IntentExtraction`, `ManagerState` (from `agents/models.py`)

### 2. Transcript Retriever (`agents/call_transcripts_agent.py`)
- **Role**: Fast direct database access (NO LLM reasoning)
- **Data flow**:
  1. SQL query to get call metadata + participants
  2. Separate HTTP requests to `/transcripts` endpoint per call ID
  3. Format into `CallTranscriptList` Pydantic model
- **API**: Gong Database REST API (fast, ~1-2 seconds)

### 3. Churn Analyzer (`agents/churn_analyzer_agent.py`)
- **Role**: LLM-powered risk assessment using Claude 4.5 Sonnet
- **Input**: `CallTranscriptList`
- **Output**: `ChurnRiskAssessment` (structured output via `with_structured_output()`)
- **Prompt**: `agents/prompts.py` - `CHURN_ANALYZER_INSTRUCTION`

### 4. Frontend (`frontend/`)
- **Tech**: FastAPI + Jinja2 + vanilla JS
- **Features**: Dark theme, Stampli branding, formatted cards for analysis/transcripts
- **Files**: `main.py`, `templates/chat.html`, `static/chat.js`, `static/style.css`

## Pydantic Models (`agents/models.py`)

```python
# Transcript data
CallTranscript: date, time, title, duration, company, stampli_contact, company_contact, gong_url, transcript
CallTranscriptList: transcripts[]

# Analysis output
RiskSignal: category, description, severity, weight_impact
NextStepRecommendation: action, rationale, urgency
ChurnRiskAssessment: churn_score (0-100), risk_level, sentiment_analysis, summary, red_flags[], signals[], recommendations[]

# Manager state
ManagerState: user_query, company_name, intent, limit, transcripts, assessment
IntentExtraction: company_name, intent (transcript|analysis), limit
```

## Database Access (`agents/tools/redshift_tools.py`)

**API Endpoints** (configured in `.env`):
- `GONG_API_BASE_URL`: `https://gong-database.stampli.cloud/gong-database`
- `GONG_API_KEY`: API key for authentication

**Key Functions**:
- `execute_query(sql)` → POST to `/query` with SQL
- `fetch_transcripts(call_ids)` → POST to `/transcripts` with call IDs (returns base64 content)
- `get_calls_for_company(company, limit)` → Uses SQL template
- `get_participants_for_calls(call_ids)` → Gets Stampli vs customer contacts
- `get_transcripts_for_company(company, limit)` → Three-step: metadata → participants → transcripts

**SQL Templates** (pre-built, no LLM reasoning):
- `latest_calls_for_company`: Gets recent calls with metadata
- `participants_for_calls`: Gets participants with `affiliation` (Internal=Stampli, External=Customer)

## Configuration (`config.py`)

```python
Settings:
  aws_region: eu-west-1
  smart_model_id: eu.anthropic.claude-sonnet-4-5-20250929-v1:0  # For analysis
  fast_model_id: eu.anthropic.claude-haiku-4-5-20251001-v1:0   # For intent
  gong_api_base_url: from GONG_API_BASE_URL env
  gong_api_key: from GONG_API_KEY env
  transcript_agent_url: http://transcript-service:8001
  churn_agent_url: http://churn-service:8002
```

## Scoring Rubric (from `agents/prompts.py`)

**Risk Levels**:
- 0-25: LOW
- 26-50: MEDIUM  
- 51-75: HIGH
- 76-100: CRITICAL

**Critical Signals (+40-50 each)**:
- Active competitor implementation → +50
- Confirmed departure → +50
- Complete product abandonment → +45
- Credentials/data transfer → +45

**High Signals (+25-35 each)**:
- Competitor evaluation → +30
- Explicit threats → +30
- Leadership pressure → +25
- Critical technical failure → +25

**Inconclusive Calls** (no real conversation):
- Wrong contact reached → +40 base
- No substantive conversation → +35 base
- Compliance issues (DNC) → +20 on top

## Docker Services (`compose.yaml`)

Each service has its own Dockerfile + pyproject.toml with **minimal dependencies** (using `uv`):

| Service | Port | Directory | Key Dependencies |
|---------|------|-----------|------------------|
| manager | 8080 | `services/manager/` | langgraph, langchain-aws, httpx |
| transcript | 8001 | `services/transcript/` | httpx only (no LLM!) |
| churn | 8002 | `services/churn/` | langchain-core, langchain-aws |
| frontend | 8000 | `services/frontend/` | httpx, jinja2 |

## API Endpoints

**Manager** (8080):
- `POST /query` - Main entry point: `{"user_query": "..."}`

**Transcript** (8001):
- `POST /retrieve` - `{"company_name": "...", "limit": 5}`

**Churn** (8002):
- `POST /analyze` - `{"transcripts": CallTranscriptList}`

**Frontend** (8000):
- `GET /` - Chat UI
- `POST /api/query` - Proxies to manager

## Running the System

```bash
# Start all services
docker-compose up -d --build

# Test transcript retrieval
curl -X POST http://localhost:8001/retrieve \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Vivo Infusion", "limit": 3}'

# Test full analysis
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "give me a churn risk analysis for Vivo Infusion"}'

# View logs
docker-compose logs -f manager-service
```

## Recent Fixes & Patterns

1. **Speed optimization**: Replaced boto3 Redshift Data API (~45s) with direct REST API (~2s)
2. **No regex parsing**: Fetch transcripts individually (1 call = 1 request) instead of parsing combined responses
3. **Smart limits**: Analysis uses 2 transcripts, transcript requests use 5
4. **Participant extraction**: Separate SQL query with `affiliation` field (Internal vs External)
5. **Time field**: Database only stores dates, so `time` shows "N/A"
6. **Structured output**: Using `ChatBedrockConverse.with_structured_output(PydanticModel)`

## File Structure

```
churn_risk_analyzer/
├── agents/
│   ├── apps/
│   │   ├── manager_app.py      # FastAPI wrapper for manager
│   │   ├── transcript_app.py   # FastAPI wrapper for retriever
│   │   └── churn_app.py        # FastAPI wrapper for analyzer
│   ├── tools/
│   │   ├── redshift_tools.py   # Database access functions
│   │   └── knowledge_files/    # Reference docs
│   ├── manager.py              # LangGraph orchestrator
│   ├── call_transcripts_agent.py  # Direct retrieval (no LLM)
│   ├── churn_analyzer_agent.py    # LLM analysis
│   ├── models.py               # All Pydantic models
│   └── prompts.py              # Churn analyzer scoring rubric
├── frontend/
│   ├── main.py                 # FastAPI frontend server
│   ├── templates/chat.html     # Chat UI template
│   └── static/
│       ├── chat.js             # Frontend JS
│       ├── style.css           # Dark theme CSS
│       └── stampli_logo.jpg    # Logo
├── services/                   # Service-specific configs (uv + pyproject.toml)
│   ├── manager/
│   │   ├── Dockerfile
│   │   └── pyproject.toml      # langgraph, langchain-aws, httpx
│   ├── transcript/
│   │   ├── Dockerfile
│   │   └── pyproject.toml      # httpx only (no LLM!)
│   ├── churn/
│   │   ├── Dockerfile
│   │   └── pyproject.toml      # langchain-core, langchain-aws
│   └── frontend/
│       ├── Dockerfile
│       └── pyproject.toml      # httpx, jinja2
├── config.py                   # Settings from .env
├── compose.yaml                # Docker Compose
├── pyproject.toml              # Dev dependencies (local dev)
└── .env                        # Environment variables (not in git)
```

## Environment Variables (.env)

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
AWS_REGION=eu-west-1
GONG_API_BASE_URL=https://gong-database.stampli.cloud/gong-database
GONG_API_KEY=...
SMART_MODEL_ID=eu.anthropic.claude-sonnet-4-5-20250929-v1:0
FAST_MODEL_ID=eu.anthropic.claude-haiku-4-5-20251001-v1:0
```

## Common Tasks

**Add new risk signal**: Edit `CHURN_ANALYZER_INSTRUCTION` in `agents/prompts.py`

**Change default transcript limit**: Edit `extract_intent()` in `agents/manager.py`

**Modify transcript parsing**: Edit `get_transcripts_for_company()` in `agents/tools/redshift_tools.py`

**Update UI styling**: Edit `frontend/static/style.css` and `frontend/static/chat.js`

**Add new Pydantic field**: Update `agents/models.py` and relevant agent code

