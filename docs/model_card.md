# RecoverAI: Model Card

## 1. Model Overview
- **Model Name**: `trend-risk-classifier`
- **Model Version**: `v1.0.0`
- **Architecture**: Balanced Random Forest Classifier (100 estimators, max depth 6)
- **Framework**: Scikit-Learn 1.5+
- **Intended Domain**: Post-Operative Remote Home Recovery Decision Support

---

## 2. Intended Use & Safety Scope
### Primary Intended Use:
- Assisting surgical teams in triaging large post-operative patient cohorts to highlight trajectories showing multi-signal persistence and deviation from personal baselines.
- Preventing cognitive alarm fatigue by suppressing isolated, self-resolving transient spikes.

### Out-of-Scope & Prohibited Use:
- **Autonomous diagnostic or prescribing systems**: The model must never prescribe medications, advise discharge, or guarantee safety without qualified clinical review.
- **Emergency triage substitute**: Acute life-threatening events (e.g., massive hemorrhage, anaphylaxis) require emergency 911/ER pathways, not asynchronous RPM telemetry.

---

## 3. Features & Inputs (14 Engineered Attributes)
1. `current_pain`: Raw pain score (0–10).
2. `current_temp`: Raw temperature (°C).
3. `current_wound_score`: Composite surgical site score (0–10).
4. `delta_pain`: Deviation from personal rolling baseline ($\Delta_{\text{pain}}$).
5. `delta_temp`: Deviation from personal rolling baseline ($\Delta_{\text{temp}}$).
6. `delta_wound`: Deviation from personal rolling baseline ($\Delta_{\text{wound}}$).
7. `pain_short_slope`: Closed-form linear rate of change over last 3 readings.
8. `temp_short_slope`: Closed-form linear rate of change over last 3 readings.
9. `wound_short_slope`: Closed-form linear rate of change over last 3 readings.
10. `persistence_count`: Consecutive worsening evaluations.
11. `multi_signal_flag`: Binary indicator (1 if $\ge 2$ agreeing worsening signals).
12. `fatigue_score`: Subjective systemic exhaustion (0–10).
13. `mobility_score`: Ambulation recovery index (0–10).
14. `data_quality_score`: Pre-processing validation confidence score (0–100).

---

## 4. Empirical Performance
Evaluated on 1,000 synthetic patient trajectories and 48,740 longitudinal observations:

| Metric | Measured Result |
| :--- | :---: |
| **Precision** | **99.6%** |
| **Recall (Sensitivity)** | **99.6%** |
| **F1-Score** | **99.6%** |
| **ROC-AUC** | **0.9993** |
| **Cohort Recall on Ground Truth** | **89.6%** |
| **Alert Reduction Achieved** | **96.5%** (Target: $\ge 30\%$) |

---

## 5. Explainability Architecture
Rather than treating risk predictions as an opaque black box, RecoverAI extracts transparent contributor weights ($W_{\text{baseline}} + W_{\text{trend}} + W_{\text{persistence}} + W_{\text{multi-signal}} + W_{\text{symptoms}} - W_{\text{quality}}$) and generates human-readable **"What Changed?"** and **"Why No Alert?"** clinical summaries for each patient.
