# RecoverAI: System Architecture

## 1. Multi-Layer Hybrid Architecture

RecoverAI implements a robust 4-tier hybrid architecture combining deterministic safety guardrails, personalized statistical time-series algorithms, an explainable machine learning classifier, and operational workflow orchestration:

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend UI                           │
│   React 19 + TypeScript + Vite + Tailwind CSS + Recharts    │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI API Gateway                      │
│   CORS Middleware • Process-Time Header • Safety Disclaimer │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Core Intelligence Engines                  │
│  1. Data Quality Engine   (Ranges, Jumps, Gaps, Quarantines)│
│  2. Personal Baseline     (Rolling median, std, baseline Δ) │
│  3. Trend & Multi-Signal  (Closed-form slopes, persistence) │
│  4. Risk & Explainability (Composite 0-100, What Changed?)  │
│  5. Alert Episode Engine  (Fatigue suppression & grouping)  │
│  6. Escalation Engine     (Task SLA, Multi-tier escalation) │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Data Storage & Machine Learning               │
│  • SQLAlchemy ORM (SQLite local / PostgreSQL production)    │
│  • Scikit-Learn Explainable Random Forest Classifier        │
│  • Model Registry (Metrics, versioning, feature weights)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Service Responsibilities

### 1. Data Quality Engine (`data_quality_engine.py`)
- Validates viable physiological bounds (Temperature: 34.0–42.5°C, Pain: 0–10).
- Identifies sudden sensor jumps ($\Delta_{\text{temp}} \ge 2.5^\circ\text{C}$, $\Delta_{\text{pain}} \ge 6.0$).
- Detects duplicate submission timestamps.
- Flags contradictory patient inputs (e.g. reported pain = 0 despite severe purulent discharge).
- Detects monitoring gaps (time elapsed since last reading > 36 hours).
- Outputs a 0–100 Data Quality Score without silently discarding unvalidated telemetry.

### 2. Personal Baseline Engine (`baseline_engine.py`)
- Computes patient-specific rolling baseline statistics ($\mu, \sigma$, median) over a stable window.
- Derives patient-specific deltas:
  $$\Delta_{\text{pain}} = \text{current} - \text{baseline}_{\text{pain}}$$
  $$\Delta_{\text{temp}} = \text{current} - \text{baseline}_{\text{temp}}$$
  $$\Delta_{\text{wound}} = \text{current} - \text{baseline}_{\text{wound}}$$

### 3. Trend Engine (`trend_engine.py`)
- Evaluates rate of change via closed-form linear regression slopes ($O(1)$ arithmetic):
  $$\text{Slope} = \frac{N\sum(i \cdot y) - \sum i \sum y}{N\sum i^2 - (\sum i)^2}$$
- Calculates persistence: counts consecutive evaluations showing progressive worsening.
- Detects multi-signal concordance: identifies when 2 or more independent physiological streams deteriorate concurrently.

### 4. Risk Engine (`risk_engine.py`)
- Derives composite 0–100 risk score based on weighted transparent contributors:
  - Baseline Deviation: up to 30 pts
  - Rate of Change: up to 25 pts
  - Persistence Counter: up to 20 pts
  - Multi-Signal Agreement: up to 15 pts
  - Symptom Severity & Concerns: up to 10 pts
  - Data Quality Penalty: -5 to 0 pts
- Generates transparent clinical summaries:
  - **"What Changed?"**: structured breakdown of deviations vs personal baseline.
  - **"Why No Alert?"**: explicit rationale explaining why isolated transient spikes are suppressed.

### 5. Alert Engine (`alert_engine.py`)
- Suppresses isolated transient variations that do not meet persistence requirements.
- Groups repeated alerts for the same patient into a single **Alert Episode** within 24 hours.
- Upgrades episode severity if a patient's trajectory escalates from Review to High Priority.

### 6. Escalation Engine (`escalation_engine.py`)
- Converts actionable alerts into clinical review tasks.
- Assigns ownership: Nurse Reviewer (2 hr SLA), Care Coordinator (6 hr SLA).
- Automatically escalates overdue tasks:
  - Level 1: Care Team Reviewer
  - Level 2: Clinical Supervisor
  - Level 3: Emergency Operations Escalation Queue
