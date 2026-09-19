# AI-Enabled Skill Intelligence & Learning Platform
### For India's Official Statistical System (MoSPI / NSO / NSSTA / iGOT Karmayogi)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.15-black.svg)](https://nextjs.org/)
[![PostgreSQL + pgvector](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![License: Open Government](https://img.shields.io/badge/License-Government_Open_Standard-orange.svg)]()

---

## 1. Executive Summary

An enterprise AI-enabled Skill Intelligence and Learning Platform engineered for the **Ministry of Statistics and Programme Implementation (MoSPI)**, **National Statistical Office (NSO)**, and **National Statistical Systems Training Academy (NSSTA)**.

### Core Architectural Principle: `LLM ≠ Competency Engine`
Competency scoring, role requirement matching, skill-gap analysis, priority weighting, and recommendation rankings are **100% deterministic, database-backed, explainable Python business logic**. AI and LLM models (Qwen3, Gemini, OpenAI, and deterministic Mock) are strictly applied for natural language tutoring, RAG grounding, explanation, and structured assessment generation.

---

## 2. The Core Intelligence Loop

```
EMPLOYEE PROFILE
       ↓
ROLE REQUIREMENTS (Statistical Officer, Survey Officer, etc.)
       ↓
ASSESSMENT (Diagnostic / Skill Verification)
       ↓
CURRENT COMPETENCY SCORE (Weighted Deterministic Evidence)
       ↓
SKILL-GAP ANALYSIS (Required - Current)
       ↓
PRIORITY WEIGHTING (Gap × Importance × Mandatory × Future Relevance)
       ↓
PERSONALIZED RECOMMENDATIONS (iGOT Karmayogi & NSSTA Programmes)
       ↓
5-STAGE LEARNING PATH (Foundation → Core → Practical → Assessment → Advanced)
       ↓
PRACTICE & GROUNDED AI TUTOR (Grounded in MoSPI / NQAF Literature)
       ↓
REASSESSMENT & CONTINUOUS IMPROVEMENT (Score increases, gap shrinks)
```

---

## 3. Technology Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2, Bcrypt, PyJWT, Python-Multipart, HTTPX
- **Database**: PostgreSQL 16 + pgvector (with SQLite fallback for instant zero-dependency local testing)
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons
- **AI & RAG**: Provider abstraction supporting Qwen3 (Ollama), Google Gemini, OpenAI, and high-fidelity Mock Provider
- **Integrations**: iGOT Karmayogi Adapter (`MockIGOTProvider` / `IGOTProvider`) and NSSTA Academy Adapter (`MockNSSTAProvider` / `NSSTAProvider`)
- **DevOps**: Docker, Docker Compose, Makefile, PowerShell startup scripts

---

## 4. Quick Start (Run Locally in 2 Minutes)

### Option A: Using Docker Compose (Recommended)
```bash
git clone <repository>
cd stat-skill-platform
cp .env.example .env
docker compose up --build
```
- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option B: Direct Local Startup (Without Docker)

#### 1. Backend Setup:
```bash
cd backend
pip install -r requirements.txt
python -m app.db.seed.seed_data
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000).

---

## 5. Pre-Seeded Demo Personas

The system comes pre-populated with realistic official statistical personas:

| Persona | Email | Password | Role / Department | Initial Gaps / Highlights |
|---|---|---|---|---|
| **Rahul Sharma** | `employee@example.com` | `demo123` | **Statistical Officer** (FOD) | **Sampling (42/80 - Critical)**, SQL (30/60 - High), Python (70/60 - Met) |
| **Priya Patel** | `trainer@example.com` | `demo123` | **Survey Officer / Faculty** (SDRD) | AI Question Generation, Assessment Review, Document Ingestion |
| **Dr. Rajesh Verma** | `admin@example.com` | `demo123` | **MoSPI Director** (NAD) | Org Heatmap, Future Skills, Training Effectiveness Delta (+21 Sampling) |

*(Instant one-click sign in buttons are available directly on the login page and top navbar).*

---

## 6. Verification & Testing

To run the automated test suite covering deterministic scoring, skill gap math, security defenses, and API routes:

```bash
cd backend
python -m pytest -v tests/
```

**15 / 15 tests pass**, verifying:
- Sampling gap calculation: `current=42, required=80 -> gap=38, status='GAP', priority='CRITICAL'`
- Python met standard: `current=70, required=60 -> gap=0, status='MET', priority='LOW'`
- Immediate competency updates upon assessment submission
- Role readiness index calculations
- RBAC and prompt injection security guards

---

## 7. Authoritative Knowledge Grounding & Authority Tiers

All learning content and AI tutor explanations are categorized into verified authority tiers:
- **Tier A**: Government of India, MoSPI, NSO, NSSTA, iGOT Karmayogi, UNSD, UNECE
- **Tier B**: OECD, World Bank, IMF, ILO, FAO
- **Tier C**: Universities, Indian Statistical Institute (ISI) Kolkata, Peer-reviewed academia
- **Tier D**: General web resources

---

## 8. Directory Layout

```
stat-skill-platform/
├── docker-compose.yml
├── .env.example
├── Makefile
├── run_demo.ps1
├── backend/
│   ├── app/
│   │   ├── api/v1/         # FastAPI REST routes
│   │   ├── core/           # Security, config, logging, exceptions
│   │   ├── db/             # SQLAlchemy engine, sessions, seed data
│   │   ├── models/         # Database entities
│   │   ├── schemas/        # Pydantic validation models
│   │   ├── services/
│   │   │   ├── competency/ # Deterministic scoring engine
│   │   │   ├── skill_gap/  # Gap & role readiness engine
│   │   │   ├── recommendations/ # Multi-factor ranking & explainer
│   │   │   ├── learning/   # 5-Stage personalized learning path
│   │   │   ├── assessments/# Evaluation & scoring stepper
│   │   │   ├── ai/         # Provider abstraction (Mock, Qwen, Gemini, OpenAI)
│   │   │   ├── rag/        # Chunking, vector search, authority ranking
│   │   │   ├── quiz/       # MCQ generator & deterministic validator
│   │   │   ├── tutor/      # Grounded conversational service
│   │   │   ├── integrations/# iGOT & NSSTA adapters
│   │   │   └── analytics/  # Heatmaps, training effectiveness, future skills
│   │   └── main.py
│   ├── tests/              # Pytest test suite
│   └── Dockerfile
└── frontend/
    ├── app/                # Next.js App Router views
    ├── components/         # Navbar, Sidebar, UI components
    ├── lib/                # Typed API client
    └── Dockerfile
```
