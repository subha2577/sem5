# RecoverAI: 3-Minute Executive Demonstration Script

## Overview
This demo script guides an evaluator through a rapid, compelling 3-minute demonstration of **RecoverAI** as a clinical operations command center.

---

### [0:00 – 0:20] The Problem: Alarm Fatigue & Missing Subtle Deterioration
- **Spoken Narration**:
  > "In traditional remote post-op monitoring, care teams ask: *'Did this reading cross a threshold?'* When an isolated reading spikes—like temporary pain after physical therapy—an alarm fires. Care teams get flooded with hundreds of false alarms, causing alarm fatigue. Meanwhile, a patient with gradual, multi-signal deterioration across pain, wound swelling, and low-grade fever gets missed. RecoverAI solves this by looking at **Trend, Change from Personal Baseline, Multi-Signal Agreement, Persistence, and Automated Escalation**."

---

### [0:20 – 0:45] Overview Command Center & Population Triage
- **Actions on Screen**:
  1. Open `http://127.0.0.1:5173/` (Overview).
  2. Point out the top banner: **96.5% Low-Value Alert Reduction Achieved** while maintaining **89.6% Sensitivity** on clinically relevant deterioration.
  3. Highlight the 8 operational KPI cards: 1,000 patients monitored, High-Priority reviews, Monitoring gaps, and Unresolved tasks.
  4. Note the pinned **Clinical Safety Notice**.

---

### [0:45 – 1:15] Signature High-Priority Patient (`REC-004`) & "What Changed?"
- **Actions on Screen**:
  1. Click the demo patient button **`REC-004` (Multi-Signal Deterioration)**.
  2. Inspect the **Longitudinal Recovery Trajectory Chart**:
     - Point out the red pain curve escalating away from the orange dashed baseline.
     - Toggle between "All Signals" and "Pain vs Baseline" / "Wound Score".
  3. Direct attention to the **Signature: What Changed?** panel:
     - Clear bullet points explaining: Pain $+4.0$ above baseline, wound concern elevated $+3.0$, and persisted across 3 consecutive evaluations.
  4. Point to the **Risk Contributor Weight Decomposition** showing exact point contributions totaling 88/100.

---

### [1:15 – 1:40] Preventing Alert Fatigue: "Why No Alert?" (`REC-002`)
- **Actions on Screen**:
  1. Return to Priority Queue and select **`REC-002` (Isolated Spike)**.
  2. Note that the patient experienced an acute pain spike (6.5) and temperature spike (38.0°C).
  3. Show the **Signature: Why No Alert?** card:
     > *"Abnormal reading detected as an isolated transient spike. Secondary recovery indicators remain stable. Persistence requirement not met. Alert suppressed from main queue to protect clinicians from alarm fatigue."*
  4. Contrast this directly with naive threshold systems which would have paged the on-call team.

---

### [1:40 – 2:10] Empirical Alert Reduction (Analytics Page)
- **Actions on Screen**:
  1. Click **Alert Analytics** in the sidebar.
  2. Show the side-by-side comparison bar chart:
     - Simple Baseline generated **15,836 alerts** (15.8 alerts per patient).
     - RecoverAI generated **555 alerts** (0.55 alerts per patient) — a **96.5% reduction** in alert burden.
  3. Show the performance table highlighting improved precision without sacrificing recall.

---

### [2:10 – 2:35] Task Ownership & Multi-Tier Escalation
- **Actions on Screen**:
  1. Click **Tasks & Escalations** in the sidebar.
  2. Point to the active tasks with assigned owners (`Nurse Sarah`, `Dr. Miller`).
  3. Show `REC-005`: Highlight the **Level 2: Clinical Supervisor** badge and **OVERDUE** timer.
  4. Click **Check Overdue Escalations** to demonstrate the automated SLA watcher in real time.
  5. Click **Resolve Task** and show the clinical note entry modal.

---

### [2:35 – 2:50] Failure State & Edge Case Handling (Data Quality Center)
- **Actions on Screen**:
  1. Click **Data Quality** in the sidebar.
  2. Point out the **Quarantined Records**: show that physiologically impossible readings (e.g. 43.5°C) are quarantined without crashing the system or corrupting baselines.
  3. Show the **Monitoring Gap** detector flagging patients who failed to submit readings for > 36 hours.

---

### [2:50 – 3:00] Simulation Sandbox & Conclusion
- **Actions on Screen**:
  1. Click **Simulation Sandbox** in the sidebar.
  2. Click **"2. Isolated Transient Spike"** $\to$ Click **Run Realtime Simulation**.
  3. Show the live Recharts graph and the side-by-side comparison card:
     - Traditional Monitoring: 1 Alert (Alarm Fatigue Risk: High).
     - RecoverAI: Alert Suppressed (Persistence not met).
  4. **Closing Statement**:
     > *"RecoverAI turns thousands of disconnected home observations into an actionable, prioritized recovery trajectory, ensuring care teams act on meaningful change without drowning in alarms."*
