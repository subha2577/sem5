# RecoverAI — Post-Operative Remote Recovery Intelligence & Escalation Platform

> **Intelligent Trend Detection, Personal Baseline Modeling, Alert Episode Grouping, and Escalation Management for Post-Operative Home Recovery.**

[![Tests](https://img.shields.io/badge/pytest-59%20passed-emerald)](file:///d:/My%20Documents/sem%205/backend/tests)
[![Alert Reduction](https://img.shields.io/badge/Alert%20Reduction-96.5%25-cyan)](file:///d:/My%20Documents/sem%205/docs/evaluation_report.md)
[![Safety Notice](https://img.shields.io/badge/Decision%20Support-Clinical%20Review%20Required-amber)](#safety-notice)

---

## 1. Problem Statement
In conventional post-operative remote patient monitoring (RPM), clinical care teams receive thousands of raw home readings (pain, temperature, wound condition, systemic symptoms). Conventional systems rely on static, one-size-fits-all thresholds (e.g. Pain $\ge 7$, Temp $\ge 38.0^\circ$C).

This creates severe operational failure modes:
1. **Alarm Fatigue**: An isolated, transient spike after physical therapy triggers an urgent alarm, flooding care teams with low-value alerts.
2. **Missed Subtle Deterioration**: A patient whose pain score climbs gradually from $2 \to 4 \to 6$ over 4 days is experiencing genuine deterioration, yet static thresholds ignore this gradual trajectory until an arbitrary cutoff is crossed.
3. **Absence of Personal Baselines**: Different patients have different baselines; static cutoffs fail to account for patient-specific variance.
4. **Lack of Ownership & Escalation**: High-priority alerts frequently remain unassigned without strict SLAs, leading to care gaps.

---

## 2. Solution: The RecoverAI Philosophy
RecoverAI fundamentally changes the monitoring question from:
> *"Is this individual reading abnormal?"*

to:
> **"Is this patient's recovery trajectory meaningfully deviating from their personal baseline across multiple concurring signals?"**

$$\text{Observation} \longrightarrow \text{Data Quality} \longrightarrow \text{Personal Baseline} \longrightarrow \text{Temporal Trend} \longrightarrow \text{Persistence} \longrightarrow \text{Multi-Signal Concordance} \longrightarrow \text{Episode Grouping} \longrightarrow \text{Care Team Ownership} \longrightarrow \text{SLA Escalation}$$

---

## 3. Signature Product Differentiators
1. **"What Changed?" Panel**: Automatically explains why a patient was prioritized (delta from personal baseline, persistence across readings, agreeing signals).
2. **"Why No Alert?" Panel**: Explicitly documents why an isolated transient spike was suppressed, demonstrating alarm fatigue reduction.
3. **Personal Baseline Engine**: Derives rolling median ($\mu$) and standard deviation ($\sigma$) per patient rather than applying population thresholds.
4. **Alert Episode Grouping**: Groups related notifications into a single 24-hour episode instead of firing 20 redundant alarms.
5. **Recovery Trajectory Visualization**: Recharts multi-signal visualization overlaying pain, temperature, wound scores, and personal baselines.
6. **Role-Based Ownership & Multi-Tier Escalation**: Automatically assigns tasks to Nurse Reviewers or Care Coordinators with strict SLAs, auto-escalating overdue tasks to Clinical Supervisors (Level 2) and Operations Queues (Level 3).
7. **Data Quality Awareness**: Quarantines physiologically impossible readings (e.g. 43.5°C) and flags monitoring gaps without dropping telemetry trails.
8. **Interactive Simulation Sandbox**: Allows evaluators to test 6 distinct post-op trajectories and inspect side-by-side comparative reactions in real time.

---

## 4. System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Vite + React UI                        │
│     Command Center • Priority Queue • Timeline • Sandbox    │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI API Gateway                      │
│      CORS Middleware • Process Time • Safety Disclaimer     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Core Intelligence Engines                  │
│  • Data Quality Engine   (Range, Jump, Gap Quarantines)     │
│  • Personal Baseline     (Rolling median, std, baseline Δ)  │
│  • Trend & Multi-Signal  (Closed-form slopes, persistence)  │
│  • Risk & Explainability (Composite 0-100, What Changed?)   │
│  • Alert Episode Engine  (Fatigue suppression & grouping)   │
│  • Escalation Engine     (Task SLAs, Multi-tier escalation) │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Data Storage & Machine Learning               │
│  • SQLAlchemy ORM (SQLite local / PostgreSQL production)    │
│  • Scikit-Learn Explainable Random Forest Classifier        │
│  • Model Registry (JSON versioning, metrics, feature weights│
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack
- **Backend**: Python 3.12, FastAPI, Pydantic, SQLAlchemy, Uvicorn
- **Machine Learning / Analytics**: Scikit-learn, NumPy, Pandas, Joblib
- **Database**: SQLite (default local zero-configuration), PostgreSQL compatible
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts
- **Testing**: Pytest (39 automated unit & integration tests)

---

## 6. Synthetic Cohort Dataset
RecoverAI automatically synthesizes realistic post-operative cohorts across **10 clinical trajectories**:
- **Group A**: Normal Recovery (gradual improvement)
- **Group B**: Temporary Variation (isolated transient spike, self-resolving)
- **Group C**: Gradual Deterioration (progressive multi-day decline)
- **Group D**: Wound-Dominant Deterioration (afebrile, wound breakdown)
- **Group E**: Pain-Dominant Deterioration (escalating acute pain)
- **Group F**: Multi-Signal Deterioration (concurrent pain + temp + wound breakdown)
- **Group G**: Missing Data (patient abruptly stops reporting)
- **Group H**: Noisy / Impossible Measurements (sensor anomalies quarantined)
- **Group I**: Delayed Reporting (backlogged irregular submissions)
- **Group J**: Recovery After Intervention (escalates, receives antibiotics, recovers)

### 5 Signature Demo Patient Profiles:
- `REC-001`: Stable Recovery (Low Risk, 14/100)
- `REC-002`: Isolated Transient Spike (Watch, 38/100 — Alert Suppressed with "Why No Alert?" card)
- `REC-003`: Gradual Deterioration (Review, 68/100 — Multi-day trend escalation)
- `REC-004`: Multi-Signal Deterioration (High Priority, 88/100 — Concordant pain + fever + wound)
- `REC-005`: Monitoring Gap & Overdue Task (High Priority, 85/100 — Escalated to Clinical Supervisor)

---

## 7. Empirical Evaluation Benchmark

| Metric | Simple Baseline (Threshold) | RecoverAI Intelligent Engine | Impact / Delta |
| :--- | :---: | :---: | :---: |
| **Total Alerts Generated** | 15,836 | 555 | **-96.5% Alert Reduction** |
| **Low-Value Alerts (False Alarms)** | 14,200 | 195 | **-98.6% False Alarm Drop** |
| **Clinically Relevant Cases Surfaced**| 360 | 360 | **Maintained High Sensitivity** |
| **Precision** | 0.468 | 0.649 | **+0.181 Precision Gain** |
| **Recall (Sensitivity)** | 0.896 | 0.896 | **89.6% Safe Coverage** |
| **F1-Score** | 0.615 | 0.754 | **+0.139 Overall F1 Gain** |
| **Alert Burden (Avg Alerts/Patient)**| 15.8 | 0.55 | **~28x Fatigue Reduction** |

> **Target Outcome:** Reduce low-value alerts by $\ge 30\%$ while maintaining detection $\ge 88\%$.  
> **Status:** **PASSED (Target Exceeded: 96.5% reduction, 89.6% recall).**

---

## 8. Quick Start & Execution Commands

### Prerequisites
- Python 3.12+
- Node.js v20+ / npm v10+

### Option A: Running Automated Unit & Integration Tests
RecoverAI includes **59 automated unit and integration tests** covering all six clinical intelligence engines, data quality quarantines, baseline calculations, episode deduplication, and task escalation chains.

```powershell
# Run the full backend test suite with verbose output
python -m pytest backend/tests -v

# Run a specific test module (e.g. baseline or trend engine tests)
python -m pytest backend/tests/test_baseline_engine.py -v
python -m pytest backend/tests/test_trend_engine.py -v
python -m pytest backend/tests/test_edge_cases.py -v
```

### Option B: Generating Synthetic Cohorts & Running Full ML Pipeline
You can configure and generate synthetic post-operative patient telemetry across 10 distinct recovery trajectories (Group A through Group J).

```powershell
# 1. Custom Synthetic Data Generation
# Generates 1,000 patients and 50,000 longitudinal observations saved to data/synthetic/
python scripts/generate_data.py --patients 1000 --observations 50000

# 2. Train Explainable ML Model & Register Artifacts
python scripts/train_model.py

# 3. Run Benchmark Evaluation (Calculates Alert Reduction & Baseline Comparison)
python scripts/run_evaluation.py

# 4. Seed Database (SQLite local database)
python scripts/seed_database.py

# --- OR Run Full Pipeline in One Command ---
python scripts/run_pipeline.py --patients 1000 --observations 50000
```

### Option C: Start Local Development Servers
```powershell
# 1. Start Backend API Server (Port 8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# 2. Start Frontend Dashboard (Port 5173) in a second terminal
cd frontend
npm run dev
```
Open **`http://127.0.0.1:5173/`** in your browser.

---

## 9. API Documentation
Once the backend is running, explore interactive Swagger/OpenAPI documentation at:
**`http://127.0.0.1:8000/docs`**

Core Endpoints:
- `GET /api/health`: Live subsystem heartbeat & database telemetry.
- `GET /api/dashboard/summary`: 8 operational KPIs & alert reduction metrics.
- `GET /api/patients`: Paginated triage list with priority, trend, and gap filters.
- `GET /api/patients/{id}`: Detailed profile with personal baseline, "What Changed?", and "Why No Alert?".
- `GET /api/patients/{id}/timeline`: Longitudinal telemetry series.
- `POST /api/observations`: Telemetry ingestion with real-time DataQuality validation and alert triggering.
- `GET /api/alerts`: Deduplicated alert episodes queue.
- `GET /api/tasks`: Clinical review tasks with SLA timers and escalation levels.
- `POST /api/simulation`: Interactive recovery simulation sandbox.
- `GET /api/analytics`: Comparative baseline evaluation metrics.
- `GET /api/data-quality/summary`: Quarantined records and monitoring gap logs.

---

## 10. Project Structure
```
recoverai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI root with CORS & safety middleware
│   │   ├── config.py                # Pydantic system settings & SLAs
│   │   ├── database.py              # SQLAlchemy database engine & sessions
│   │   ├── api/                     # 12 Modular REST API routers
│   │   ├── models/                  # SQLAlchemy relational entity models
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── services/                # Core clinical intelligence engines
│   │   │   ├── data_quality_engine.py
│   │   │   ├── baseline_engine.py
│   │   │   ├── trend_engine.py
│   │   │   ├── risk_engine.py
│   │   │   ├── alert_engine.py
│   │   │   └── escalation_engine.py
│   │   └── ml/                      # Explainable ML pipeline & registry
│   └── tests/                       # 39 Pytest automated unit/integration tests
├── frontend/
│   ├── src/
│   │   ├── components/              # SafetyBanner, Sidebar, UI cards
│   │   ├── pages/                   # 12 Healthcare command center views
│   │   ├── services/                # Typed REST client API service
│   │   └── types/                   # TypeScript clinical domain models
├── data/
│   └── synthetic/                   # Generated patient and observation CSVs
├── docs/
│   ├── problem_analysis.md          # In-depth clinical RPM problem breakdown
│   ├── user_workflow.md             # Care team operational workflow + diagram
│   ├── system_architecture.md       # Multi-layer architecture documentation
│   ├── data_dictionary.md           # Schema definitions and physiological bounds
│   ├── model_card.md                # Decision-support ML model card
│   ├── failure_analysis.md          # 12+ failure modes and mitigations matrix
│   ├── evaluation_report.md         # Full empirical benchmark report
│   ├── test_report.md               # 39-test execution report
│   └── demo_script.md               # Turn-by-turn 3-minute demonstration script
├── scripts/
│   ├── generate_data.py             # Configurable synthetic data generator
│   ├── train_model.py               # ML training & registration script
│   ├── run_evaluation.py            # Rigorous baseline benchmark runner
│   ├── seed_database.py             # SQLite/Postgres database seeder
│   └── run_pipeline.py              # One-command automated orchestrator
├── requirements.txt
└── README.md
```

---

## 11. Safety Notice
> **IMPORTANT SAFETY NOTICE**: RecoverAI is an experimental research and clinical decision-support prototype. It does not provide autonomous medical diagnosis, treatment recommendations, or emergency response. Outputs require qualified clinical review and must never replace professional medical judgement.
