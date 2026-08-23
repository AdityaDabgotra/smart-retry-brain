<div align="center">

# 🧠 Smart Retry Brain

### An intelligent payment retry system that understands *why* a payment failed — and decides the smartest way to recover it.

Modeled on Razorpay's own **Smart Retry** feature.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Ollama](https://img.shields.io/badge/Qwen2.5-via_Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Overview](#-the-problem) · [Results](#-results) · [Architecture](#-architecture) · [Setup](#-running-it) · [Usage Flow](#-how-it-works-end-to-end) · [API](#-api-reference) · [Design Notes](#-design-decisions-worth-asking-about)

</div>

---

## 📌 The Problem

Payments fail for very different reasons — a network blip, an expired card, a wrong OTP, insufficient funds — but most systems retry **all of them the same way**, or not at all.

That's a bad trade twice over:

- It **wastes retry attempts** on failures a retry can never fix (a wrong OTP doesn't magically become right the second time).
- It **misses easy wins** — like a card that's expired, which will never work no matter how many times you retry it on the same card, but recovers instantly on a different channel.

**Smart Retry Brain** reads the actual failure reason, classifies it, and decides — per category — whether to retry immediately, retry later, switch payment channel, or leave it for the customer to fix.

---

## 📊 Results

Tested on a synthetic dataset of **1,000 realistic failed transactions**, benchmarked against a naive "retry everything, every hour, blindly" baseline:

<div align="center">

| Metric | 🧠 Smart | 🔁 Naive (hourly, blind) |
|---|:---:|:---:|
| **Recovered revenue** | ₹1,61,12,840 | ₹1,48,43,182 |
| **Transactions recovered** | 731 / 1,000 | 681 / 1,000 |
| **Total retry attempts used** | 1,601 | 2,025 |

### 🟢 ₹12,69,658 more revenue recovered — using 424 fewer retry attempts

</div>

> The naive baseline uses the **exact same simulated bank success rates** as the smart engine — the only thing that differs is the *decision logic*, not the underlying odds. The comparison isn't rigged.

---

## 🏗 Architecture

```
                         Failed payment (webhook)
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │   Rule Engine (regex)      │
                    │   fast, deterministic,     │
                    │   handles known patterns   │
                    └───────────────────────────┘
                                    │
                     confident match?      no match
                          │                   │
                          ▼                   ▼
                    Classified      ┌───────────────────────────┐
                          │         │  Qwen2.5 (via Ollama)      │
                          │         │  few-shot LLM classifier   │
                          │         │  for ambiguous cases       │
                          │         └───────────────────────────┘
                          │                   │
                          └─────────┬─────────┘
                                    ▼
                    ┌───────────────────────────┐
                    │      Decision Engine        │
                    │  category → action:         │
                    │  • retry now                │
                    │  • retry later (avoid        │
                    │    bank downtime windows)    │
                    │  • switch channel             │
                    │  • flag for manual review     │
                    └───────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                ▼                                         ▼
    ┌───────────────────────┐              ┌───────────────────────────┐
    │  Qwen explains the     │              │   APScheduler fires the    │
    │  decision in plain      │              │   retry against a          │
    │  English for the        │              │   simulated bank at the    │
    │  merchant dashboard     │              │   scheduled time            │
    └───────────────────────┘              └───────────────────────────┘
                                                        │
                                                        ▼
                                    Recovered ✅ · Failed ❌ · Needs review ⚠️
```

**Stack**

| Layer | Technology |
|---|---|
| API | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Queue / cache | Redis |
| Scheduler | APScheduler |
| Classification / explanation | Qwen2.5, self-hosted via Ollama — **pluggable to Claude or OpenAI in one line** |
| Frontend | Next.js 15 + Tailwind v4 |
| Package management | `uv` |

---

## 🔌 Why the LLM Provider Is Pluggable

Swapping the LLM provider — Qwen → Claude → GPT — requires changing **exactly one config value**:

```env
# backend/.env
RETRY_BRAIN_LLM_PROVIDER=huggingface   # huggingface | anthropic | openai
```

Every provider implements the same interface (`app/llm/base.py`), so nothing else in the codebase touches the model choice. Started with a free, self-hosted model (Qwen2.5 via Ollama) specifically so classification and explanation never depend on a paid API key or an external rate limit mid-demo.

---

## ⚙️ How It Works, End to End

1. **A payment fails** → a webhook hits `POST /webhooks/payment-failed` with a Razorpay-style payload (`error_code`, `error_description`, `amount`, `payment_method`, etc.)
2. **Classification kicks off automatically** in the background: the rule engine tries first; if the failure description is ambiguous, Qwen2.5 classifies it with reasoning
3. **The decision engine** maps the category to an action — immediate retry, scheduled retry (avoiding known bank downtime windows), channel switch, or "needs the customer's attention"
4. **Qwen writes a plain-English explanation** of the decision for the merchant dashboard — no raw error codes shown to a human
5. **APScheduler polls every 5 seconds**, and fires any retry that's due against a simulated bank (with realistic, category-specific success rates)
6. **The dashboard** shows the live recovery ledger: revenue recovered vs. the naive baseline, a category breakdown, and the transaction-level audit trail

---

## 🚀 Running It

**Requires:** Docker Desktop, Node.js, and [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/AdityaDabgotra/smart-retry-brain.git
cd smart-retry-brain
```

### 1. Start infrastructure

```bash
docker compose up -d postgres redis ollama
docker exec -it smart-retry-brain-ollama-1 ollama pull qwen2.5:3b
```

### 2. Backend

```bash
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```
*(keep this terminal running)*

### 3. Seed demo data — new terminal

```bash
cd backend
uv run python scripts/seed_demo.py
```

### 4. Start the retry scheduler — new terminal

```bash
cd backend
uv run python scripts/run_scheduler.py
```

### 5. Frontend — new terminal

```bash
cd frontend
npm install
npm run dev
```

**Dashboard:** [http://localhost:3000](http://localhost:3000)
**API docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/webhooks/payment-failed` | Ingest a failed payment event |
| `GET` | `/transactions?limit=50` | List recent transactions with classification, decision, and explanation |
| `GET` | `/analytics/summary` | Smart vs. naive recovered revenue, attempts, and uplift |
| `GET` | `/health` | Liveness check + active LLM provider |

---

## 🧪 Testing

```bash
cd backend
uv run pytest tests/ -v
```

---

## 💡 Design Decisions Worth Asking About

- **Rule engine before LLM, not instead of it.** Deterministic regex patterns handle the ~95% of failures with well-known descriptions; the LLM only spends compute on genuinely ambiguous cases. Cheaper, faster, and more predictable than classifying everything with an LLM.
- **`UNKNOWN` is a first-class outcome, not an error.** The system only auto-decides what it's confident about. Low-confidence cases route to manual merchant review *with the model's reasoning attached*, rather than silently guessing.
- **The naive baseline isn't a strawman.** It uses the same bank simulator and the same success probabilities as the smart engine — the only variable that changes is the decision strategy, keeping the ₹12.69L uplift figure honest.
- **Bank-downtime-aware scheduling.** Scheduled retries are deliberately shifted away from a known low-success window (2–4 AM) rather than fired blindly.

## ⚠️ Known Limitation

The retry scheduler currently runs as a standalone long-lived process rather than a managed job queue (Celery/cron/Lambda). That's a reasonable simplification for a demo — a production deployment would move it to a proper worker system.

---

## 📄 License

MIT © 2026 [Aditya Dabgotra](https://github.com/AdityaDabgotra) — see [LICENSE](LICENSE).

</div>