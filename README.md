# Enterprise IT Support Agentic RAG Copilot

An end-to-end **Forward Deployed Engineer (FDE) project** that turns a notebook-style Agentic RAG workflow into a deployable internal product using **LangGraph, FastAPI, FAISS, Gemini (free tier), DuckDuckGo, HTML, CSS, and JavaScript**.

**100% free. No paid API. No Ollama. No local model download.** One free Google key runs the whole thing; an optional free Groq key acts as automatic fallback.

### 🔗 Live Demo

**https://it-support-agentic-rag.onrender.com**

Deployed straight from this repo on Render (free tier) using the included `Dockerfile` + `render.yaml` Blueprint. The free instance sleeps after 15 minutes of inactivity, so the first request can take ~30–60 seconds to wake up.

---

## 1. Business Problem

### Customer
**NovaRetail**, a fictional 3,000-employee retail company.

### Problem
The internal IT team maintains many documents: VPN instructions, password rules, MFA policy, software installation rules, laptop troubleshooting guides, and service-desk runbooks.

Employees still create repetitive support tickets because:

- They do not know where the correct document is.
- Traditional keyword search returns too many results.
- A normal chatbot may hallucinate an answer.
- Internal documents can be incomplete or outdated.
- Some questions require current vendor information from the public web.

### Example
An employee asks:

> **“How do I connect to the company VPN from home?”**

The answer exists in the private company KB, so the system should **not search the public internet**.

Another employee asks:

> **“What is the latest Microsoft Teams outage guidance?”**

The internal KB may not contain current outage information. The system should recognize weak private evidence, use an external search, grade that evidence, and answer with an external-source warning.

### Business Goal
Build a secure IT Support Copilot that:

1. Searches trusted private knowledge first.
2. Checks whether retrieved evidence is good enough.
3. Uses web search only when private knowledge is insufficient.
4. Rewrites weak queries and retries.
5. Generates grounded answers.
6. Shows the decision path for transparency and debugging.
7. Lets authorized staff add new company documents.

---

## 2. Why This Is an FDE Project

A Forward Deployed Engineer does more than create an LLM notebook. The FDE must turn the customer's problem into a usable product.

```text
Customer Problem
      ↓
Discovery & Requirements
      ↓
Solution Architecture
      ↓
Data / Knowledge Integration
      ↓
Agentic RAG Development
      ↓
API Development
      ↓
User Interface
      ↓
Security + Audit + Testing
      ↓
Deployment
      ↓
Observe + Improve
```

This repository demonstrates each layer.

---

## 3. Simple Architecture

```text
                   ┌─────────────────────┐
                   │   Employee / User   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ HTML/CSS/JavaScript │
                   │      Web UI         │
                   └──────────┬──────────┘
                              │ POST /api/chat
                              ▼
                   ┌─────────────────────┐
                   │       FastAPI       │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │     LangGraph       │
                   │ Agentic RAG Control │
                   └──────────┬──────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
       ┌───────────────┐              ┌──────────────┐
       │ Private KB    │              │ DuckDuckGo   │
       │ FAISS local   │              │ Search       │
       └───────┬───────┘              └──────┬───────┘
               │                             │
               └──────────────┬──────────────┘
                              ▼
                     ┌────────────────┐
                     │ Gemini LLM     │
                     │ Grounded Answer│
                     └────────────────┘
```

---

## 4. Agentic RAG Workflow

```text
Question
   ↓
[1] Route Question
   ├── Greeting / simple chat ─────────────→ Direct Answer
   │
   └── IT support question
                ↓
[2] Retrieve from Private FAISS KB
                ↓
[3] Grade Private Evidence
       ┌────────┴────────┐
       │                 │
     GOOD               WEAK
       │                 │
       ▼                 ▼
Generate from KB    [4] DuckDuckGo Web Search
                         ↓
                  [5] Grade Web Evidence
                    ┌────┴─────┐
                    │          │
                  GOOD        WEAK
                    │          │
                    ▼          ▼
              Generate Web  [6] Rewrite Query
                               ↓
                         Retry Private KB
                               ↓
                        Max retry reached?
                               ↓
                    Insufficient Evidence
```

### Why Agentic?

Normal RAG does approximately this:

```text
Question → Retrieve → Generate
```

This project makes decisions:

```text
Question
 → Route
 → Retrieve
 → Evaluate evidence
 → Choose KB or Web
 → Rewrite if needed
 → Retry
 → Generate grounded answer
```

The system therefore controls **what to do next** based on its current state.

---

## 5. Main Technology Stack (all free)

| Layer | Technology | Purpose | Cost |
|---|---|---|---|
| Agent workflow | LangGraph | Stateful routing and conditional decisions | Free |
| LLM | Gemini Flash-Lite (`gemini-flash-lite-latest`) | Routing, grading, rewriting, answer generation | Free tier, no card |
| LLM fallback | Groq `openai/gpt-oss-20b` | Automatic failover when Gemini quota is exhausted | Free tier, no card |
| Embeddings | Gemini `gemini-embedding-001` | Cloud embeddings, no local download | Free tier, no card |
| Vector DB | FAISS (local file) | Private enterprise knowledge base, no server/key | Free |
| External search | DuckDuckGo | Fallback when company KB is insufficient | Free, no key |
| API | FastAPI | Backend and REST endpoints | Free |
| Frontend | HTML/CSS/JavaScript | Employee-facing interface | Free |
| Audit | SQLite | Basic decision-path logging | Free |
| Packaging | Docker | Reproducible deployment | Free |

---

## 6. Project Structure

```text
Enterprise-IT-Support-Agentic-RAG-Copilot/
│
├── app/
│   ├── api/
│   │   └── routes.py              # Chat, health and ingestion APIs
│   │
│   ├── core/
│   │   ├── config.py              # Environment configuration (free-tier settings)
│   │   ├── keypool.py             # Multi-key round-robin rotation
│   │   └── logging.py             # Logging configuration
│   │
│   ├── rag/
│   │   ├── state.py               # LangGraph state + structured decisions
│   │   ├── vectorstore.py         # FAISS + Gemini embeddings
│   │   └── workflow.py            # Complete Agentic RAG graph (+ Groq failover)
│   │
│   ├── services/
│   │   ├── audit.py               # SQLite query audit
│   │   └── ingestion.py           # PDF/TXT/MD/DOCX loading + chunking
│   │
│   └── main.py                    # FastAPI application (+ boot auto-ingest)
│
├── data/
│   └── sample_kb/
│       ├── company_it_handbook.md
│       └── service_desk_runbook.md
│
├── static/
│   ├── css/style.css
│   └── js/app.js
│
├── templates/
│   └── index.html
│
├── render.yaml                    # Render Blueprint (one-click deploy)
├── Dockerfile                     # Production container
├── .env.example                   # Free-key env template (copy to .env)
├── ingest_sample_kb.py            # Load sample docs into FAISS
├── requirements.txt
├── run.py                         # Local entry point (port 8080)
└── README.md
```

---

## 7. Setup (fresh PC: clone → run in 10 minutes)

### Prerequisites

- **Python 3.11+** ([python.org](https://www.python.org/downloads/)) — check with `python --version`
- **Git**
- (Optional, only for container runs) **Docker Desktop**

### Step 1 — Clone

```bash
git clone https://github.com/fahim3101/Agentic-Rag-System.git
cd Agentic-Rag-System
```

### Step 2 — Virtual environment (recommended)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Get free API keys (no credit card anywhere)

1. **Gemini key (required — LLM + embeddings):** go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → Create API key → copy it.
2. **Groq key (optional but recommended — automatic fallback):** go to [console.groq.com](https://console.groq.com) → API Keys → create one.

### Step 5 — Configure environment

Copy the template and fill in your keys:

```bash
# Windows
copy .env.example .env
# macOS/Linux
cp .env.example .env
```

Edit `.env`:

```env
# Required: one or more Gemini keys (comma-separated = auto-rotated)
GOOGLE_API_KEYS=AIza_paste_your_key_here

# Optional fallback
GROQ_API_KEY=gsk_paste_your_key_here
```

> `ADMIN_API_KEY` can stay as-is for local use. Never commit `.env` — it is already in `.gitignore`.

#### Environment Variable Reference

| Variable | Description | Required |
|---|---|---|
| `GOOGLE_API_KEYS` | Free Google AI Studio key(s), comma-separated for rotation | ✅ Yes |
| `GROQ_API_KEY` | Free Groq key, used only when Gemini quota is exhausted | Optional |
| `GEMINI_MODEL` | Default: `gemini-flash-lite-latest` | Optional |
| `EMBEDDING_MODEL` | Default: `models/gemini-embedding-001` | Optional |
| `GROQ_MODEL` | Default: `openai/gpt-oss-20b` | Optional |
| `ADMIN_API_KEY` | Secret for the document-upload endpoint | Optional (change in production) |
| `APP_ENV` | `development` or `production` | Optional |

### Step 6 — Load sample company knowledge

```bash
python ingest_sample_kb.py
```

Expected output:

```text
Indexed 2 files -> 5 chunks -> FAISS .../data/faiss_index
```

Pipeline:

```text
Company Documents
   ↓
Load Documents
   ↓
Chunk Text
   ↓
Gemini Embeddings (free API)
   ↓
FAISS Local Vector Database
```

### Step 7 — Run the application

```bash
python run.py
```

Open:

```text
http://127.0.0.1:8080
```

FastAPI API docs:

```text
http://127.0.0.1:8080/docs
```

Stop anytime with `Ctrl+C`.

---

## 8. Classroom Demo Scenarios

### Demo A — Private KB Success

Ask:

> **How do I connect to the company VPN from home?**

Expected path:

```text
Router → KB
Private KB Retrieval
KB Grade → GOOD
Generate from Private KB
```

Teaching point:

> Trusted internal company knowledge is preferred. No public web call is necessary.

---

### Demo B — Company Policy Question

Ask:

> **Can IT support ask me to share my MFA code?**

The internal handbook says employees must never share passwords or MFA codes with support personnel.

Expected path:

```text
Router → KB
Private KB Retrieval
KB Grade → GOOD
Private KB Answer
```

Teaching point:

> RAG allows the model to answer using company-specific information it was never trained on.

---

### Demo C — External / Current Information

Ask:

> **What is the latest Microsoft Teams outage guidance?**

Expected path when internal documents do not answer it:

```text
Router → KB
Private KB Retrieval
KB Grade → WEAK
DuckDuckGo Search
Web Grade → GOOD
Web Answer
```

Teaching point:

> Agentic RAG can choose another information source rather than blindly answering from irrelevant vectors.

---

### Demo D — Query Rewrite

Ask a deliberately vague question such as:

> **My work communication app is acting strange after the new update. What should I do?**

If both KB and first external retrieval are weak, the workflow can rewrite the query and retry.

Teaching point:

> Retrieval failure does not immediately mean failure. An agent can improve the search query and try again while using a retry guard to avoid loops.

---

### Demo E — Direct Conversation

Ask:

> **Hello!**

Expected path:

```text
Router → DIRECT
Direct Answer
```

Teaching point:

> Not every message should trigger expensive vector search or web search.

---

## 9. Document Upload Demo

The sidebar contains **Add Company Document**.

Use the `ADMIN_API_KEY` from `.env`.

Upload one of:

- `.pdf`
- `.txt`
- `.md`
- `.docx`

The backend performs:

```text
Upload
  ↓
Validate Type
  ↓
Load Text
  ↓
Recursive Chunking
  ↓
Gemini Embeddings (free)
  ↓
FAISS Local Indexing
  ↓
Immediately Available for Retrieval
```

This is useful in an FDE demonstration because the customer does not want to edit Python every time a new policy is published.

---

## 10. API Endpoints

### `GET /api/health`

Health check.

### `POST /api/chat`

Request:

```json
{
  "question": "How do I reset my company password?"
}
```

Response contains:

```json
{
  "answer": "...",
  "source_used": "private_kb",
  "trace": [
    "Router → KB",
    "Private KB retrieval → 4 chunks",
    "KB evidence grade → GOOD",
    "Answer generation → PRIVATE KB"
  ],
  "citations": []
}
```

### `POST /api/ingest`

Protected by the `X-Admin-Key` request header.

Uploads a document and adds its chunks to local FAISS.

---

## 11. Free-Tier Quotas (read this before heavy testing)

- Each full chat costs **3–6 LLM calls**. A greeting costs 1.
- Gemini free tier is roughly **20 requests/day per model** — one key supports ~3–4 full RAG chats/day.
- Need more? Add a 2nd/3rd free key: `GOOGLE_API_KEYS=key1,key2,key3` (auto-rotated), and/or set `GROQ_API_KEY` for automatic failover.
- A `429 RESOURCE_EXHAUSTED` error means that model's daily quota is done — wait a few hours or add keys.

---

## 12. Deploy to Render (live link in ~5 minutes)

The repo ships with `render.yaml` (Blueprint) and a tested `Dockerfile`.

> **Live instance:** https://it-support-agentic-rag.onrender.com
> Deployed from this repo — after a `git push`, use **Manual Deploy → Deploy latest commit** to redeploy.

1. Go to **dashboard.render.com → New + → Blueprint**, connect the GitHub repo, Apply.
2. Fill `GOOGLE_API_KEYS` and `GROQ_API_KEY` in the Environment tab (`ADMIN_API_KEY` auto-generates).
3. **Deploy Blueprint** → wait 3–6 min → live URL appears.
4. Notes: free instances sleep after 15 min idle (first request wakes in ~1 min); no persistent disk on free, but the app **auto-rebuilds the FAISS index on boot** if keys are set.

---

## 13. Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `GOOGLE_API_KEY(S) is missing` | `.env` missing or empty — copy `.env.example` to `.env` and add your key |
| `429 RESOURCE_EXHAUSTED` / quota error | Daily free quota done — wait, or add more keys / `GROQ_API_KEY` |
| `FAISS index not found` | Run `python ingest_sample_kb.py` first |
| `Address already in use :8080` | An old server still holds the port — stop other terminals / kill leftover `python run.py` processes |
| UI shows old errors after a code fix | Hard-refresh the browser (`Ctrl+F5`); HTML/JS/CSS changes need no server restart, `.py`/`.env` changes need a restart |
| Page text looks like symbols | Browser font setting (e.g. Wingdings) — reset `chrome://settings/fonts` to Arial/Times |
| Live site slow / `503` on first hit | Free Render instance was asleep — the first request wakes it (~30–60 s), later ones are fast |

---
