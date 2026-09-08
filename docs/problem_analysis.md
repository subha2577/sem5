# RecoverAI — Problem Analysis

## 1. Operational Problem

Post-operative patients are discharged home earlier than ever due to healthcare capacity pressure. Surgical teams now rely on **remote patient monitoring (RPM)** — patients self-report pain scores, temperatures, and wound observations from home via mobile apps or SMS.

This transition creates a severe operational failure:

> Care teams receive thousands of raw home readings but cannot determine which observations represent genuine clinical deterioration and which are low-value transient fluctuations.

---

## 2. Current State Pain Points

### 2.1 Alarm Fatigue
Conventional monitoring applies static, population-level thresholds (e.g. Pain >= 7/10, Temperature >= 38.0°C). Any single reading that crosses a threshold fires an alert — regardless of context, patient history, or whether the reading is isolated or part of a worsening pattern.

**Result**: A 1,000-patient cohort generates approximately 15,836 alerts per monitoring cycle. Care teams cannot meaningfully respond to this volume.

### 2.2 Missed Gradual Deterioration
A patient whose pain score climbs from 2 → 4 → 6 over 4 days is experiencing genuine clinical deterioration. Static thresholds do not detect this gradual trajectory until an arbitrary fixed cutoff is finally exceeded — by which point the clinical window for early intervention may have passed.

### 2.3 No Patient-Specific Baselines
An elderly patient recovering from knee replacement surgery has a different pain baseline than a healthy 30-year-old recovering from laparoscopic cholecystectomy. Static population cutoffs treat all patients identically, generating both false positives (alerts on patients with naturally higher baselines) and false negatives (missing deterioration in patients with naturally low baselines).

### 2.4 Isolated Signal Blindness
True post-operative complications (surgical site infection, anastomotic leak, pulmonary embolism) rarely manifest in a single metric. They present as **concordant multi-signal movement**: escalating pain, low-grade fever, and wound inflammation occurring simultaneously over multiple observations. Single-signal alerting misses this clinical pattern entirely.

### 2.5 Unresolved Ownership and Escalation Gaps
Alerts generated without explicit owners, due dates, or escalation pathways are frequently ignored during shift transitions. High-priority deteriorations can remain unreviewed for hours while staff are occupied with in-patient responsibilities.

---

## 3. Consequences

| Consequence | Clinical Impact |
|:---|:---|
| Alert fatigue | Care team stops reading alerts; genuine deterioration ignored |
| Missed gradual deterioration | Patient admitted to emergency with preventable complication |
| False alarms for stable patients | Unnecessary clinical contact; patient anxiety; staff time wasted |
| Ownership gap | Deteriorating patient receives no timely intervention during shift change |
| Silent monitoring gap | Patient stops reporting; system assumes stable; missed deterioration |

---

## 4. Users Affected

| User | Pain Point |
|:---|:---|
| **Nurse Reviewer** | Receives 15-20 alerts/patient/week; cannot review all meaningfully |
| **Care Coordinator** | Relies on manual file review to spot monitoring gaps |
| **Clinical Supervisor** | No visibility into unresolved escalations across team |
| **Patient (home)** | Receives unnecessary call-backs for isolated harmless readings |
| **Clinical Operations** | No measurable alert quality metric; cannot assess system performance |

---

## 5. Problem Statement (Formal)

> Post-operative patients report pain, temperature, and wound observations from home. The organisation needs a solution because care teams receive too many low-value readings and miss meaningful changes.
>
> The system must translate the operational problem into a **trend summariser** that **prioritises meaningful change over individual abnormal readings**.

---

## 6. Proposed Solution: RecoverAI Philosophy

RecoverAI rejects the naive monitoring paradigm:

```
Reading --> Fixed Threshold --> Alert
```

In its place, RecoverAI implements a multi-dimensional clinical decision-support framework:

```
Observation
  --> Data Quality Validation
  --> Patient-Specific Baseline Computation
  --> Temporal Trend Analysis (slope + persistence)
  --> Multi-Signal Concordance Check
  --> Episode Deduplication and Grouping
  --> Composite Risk Scoring with Explainability
  --> Care Team Ownership Assignment
  --> SLA-Driven Escalation
```

**The core question changes from:**
> "Is this reading outside a fixed threshold?"

**To:**
> "Has this patient's recovery trajectory meaningfully changed from their personal baseline, persistently, across multiple concordant signals?"

---

## 7. Measurable Impact Goals

| Goal | Target | Achieved (Synthetic) |
|:---|:---|:---|
| Reduce low-value alerts | >= 30% reduction | 96.5% reduction |
| Maintain clinical sensitivity | >= 88% recall | 89.6% recall |
| Explainability | Every alert explains WHY | "What Changed?" + "Why No Alert?" panels |
| Ownership | Every alert has named owner + SLA | Implemented via EscalationEngine |
| Unresolved action tracking | No high-priority case silently disappears | Level 3 escalation queue; Overdue badge |

---

## 8. Scope and Constraints

**In Scope (Prototype):**
- Pain, temperature, wound observations from synthetic home data
- Symptom reports (patient_reported_concern: None/Mild/Moderate/Severe)
- Patient-specific baselines
- Trend summarisation
- Alert episode grouping and deduplication
- Three-tier escalation
- Failure mode documentation

**Out of Scope (Prototype):**
- Real patient data (all synthetic)
- Real-time sensor streaming
- Wound photograph analysis
- Medication management
- Emergency dispatch integration
- Regulatory approval

---

## 9. Clinical Safety Statement

This prototype is a decision-support tool for human review. It does not diagnose patients, prescribe treatment, or provide autonomous emergency response. All outputs are advisory and require qualified clinical review before any action is taken.
