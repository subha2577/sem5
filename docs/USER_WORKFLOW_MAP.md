# RecoverAI — User and Workflow Map

## 1. Operational Problem

Post-operative patients report pain, temperature, and wound observations from home. Care teams face:
- **Alarm fatigue**: Static thresholds generate thousands of low-value alerts per week
- **Missed gradual deterioration**: Slow multi-day worsening goes undetected until a threshold is finally crossed
- **No personal baseline**: One-size-fits-all cutoffs ignore patient-specific recovery baselines
- **Ownership gaps**: Alerts without assigned owners and due dates go unresolved at shift transitions

---

## 2. Current Workflow (Before RecoverAI)

```
Patient at home
  |
  v
Submits pain score, temperature, wound observation
  |
  v
Static threshold check
  IF reading >= fixed cutoff
    --> ALERT FIRES (regardless of patient history or context)
    --> Added to shared alert queue (no owner assigned)
    --> Often unreviewed during shift change
  ELSE
    --> No alert (even if gradual multi-day deterioration is occurring)
```

**Pain points:**
- Nurse receives 15-20 alerts per patient per week
- 96%+ of alerts are low-value transient spikes
- Genuine deterioration masked by alert fatigue
- No tracking of unresolved alerts
- No automatic escalation if ignored

---

## 3. Proposed Workflow (RecoverAI)

```
Patient at home
  |
  v
Submits observation (pain, temperature, wound, symptoms) via Mobile App / SMS
  |
  v
[1] DATA QUALITY ENGINE
  - Validates physiological ranges (pain 0-10, temp 34-42.5°C)
  - Checks for impossible values, sudden jumps, duplicates, contradictions
  - Quarantines invalid readings (no false clinical alerts from bad data)
  - Detects monitoring gaps (>36h without submission)
  |
  v
[2] PERSONAL BASELINE ENGINE
  - Derives patient-specific rolling baseline from prior valid observations
  - Computes rolling median and standard deviation per signal
  - Flags baseline_uncertain for patients with fewer than 3 valid observations
  - Calculates deviation from personal baseline (not population cutoff)
  |
  v
[3] TREND & MULTI-SIGNAL ENGINE
  - Computes short-term (3-obs) and medium-term (7-obs) slopes per signal
  - Counts persistence: consecutive worsening observations
  - Detects multi-signal agreement: 2+ signals concordantly worsening
  - Classifies trajectory: Stable / Improving / Worsening / Mixed
  |
  v
[4] RISK & EXPLAINABILITY ENGINE
  - Composite risk score 0-100 from:
      Baseline deviation (30 pts)
      Rate of change (25 pts)
      Persistence (20 pts)
      Multi-signal agreement (15 pts)
      Symptom severity (10 pts)
  - Generates "What Changed?" bullet summary
  - Generates "Why No Alert?" explanation for suppressed events
  - Classifies: Stable / Watch / Review / High Priority
  |
  v
[5] ALERT ENGINE
  - IF isolated single spike (Watch, persistence < 2, no multi-signal):
      --> Suppress alert from main queue
      --> Generate "Why No Alert?" card
      --> Log suppressed event for audit
  - IF persistent or multi-signal deterioration (Review / High Priority):
      --> Create or update Alert Episode (deduplication)
      --> Episode groups related alerts within 24h window
  |
  v
[6] ESCALATION ENGINE (Task + SLA)
  - Creates clinical follow-up task for every unsuppressed alert
  - Assigns owner (Nurse Reviewer for High Priority, Care Coordinator for Review)
  - Sets due_at timestamp (High Priority: 2h SLA, Review: 6h SLA)
  - If now > due_at AND status != Resolved:
      Level 1 (Nurse) --> Level 2 (Clinical Supervisor, +2h SLA)
      Level 2 --> Level 3 (Operations Queue, +1h SLA)
  - Overdue tasks remain permanently visible; cannot be silently dismissed
  |
  v
[7] CARE TEAM DASHBOARD
  - Priority Queue shows all active tasks with owner, due time, escalation level
  - Patient Detail shows timeline, baselines, trend summary, escalation history
  - Monitoring Gaps panel shows patients who stopped reporting
  - Data Quality panel shows quarantined records
  - Analytics shows Baseline vs RecoverAI comparison
```

---

## 4. Before vs After Comparison

| Aspect | Before (Static Threshold) | After (RecoverAI) |
|:---|:---|:---|
| Alert trigger | Any reading >= fixed cutoff | Persistent multi-signal deviation from personal baseline |
| Patient baseline | Population average | Patient-specific rolling median |
| Transient spike | Generates alert | Suppressed with "Why No Alert?" explanation |
| Gradual deterioration | Missed until threshold crossed | Detected via slope + persistence |
| Alert volume | ~15.8 alerts/patient | ~0.55 alerts/patient (96.5% reduction) |
| Ownership | Shared queue, no assigned owner | Named owner with SLA timer |
| Escalation | Manual, ad hoc | Automated Level 1→2→3 escalation |
| Missing data | Silent (assumed stable) | Monitoring gap flag + follow-up task |
| Invalid data | May generate false alert | Quarantined; no alert |
| Explainability | None | "What Changed?" + "Why No Alert?" panels |

---

## 5. Care Team Roles and Responsibilities

| Role | System Persona | Primary Responsibility | SLA |
|:---|:---|:---|:---|
| **Patient (home)** | Submitter | Reports pain, temperature, wound observations via app or SMS | Daily or as instructed |
| **Care Coordinator** | Coordinator Alex | Reviews Watch/Review patients, manages monitoring gaps, outreach | 6h for Review tasks |
| **Nurse Reviewer** | Nurse Sarah | Investigates High Priority alerts, reviews What Changed summary, contacts patient | 2h for High Priority tasks |
| **Clinical Supervisor** | Dr. Miller | Receives Level 2 escalated overdue tasks, directs clinical interventions | Acts on escalated tasks immediately |
| **Escalation Manager** | Operations Queue | Receives Level 3 tasks when supervisor also misses SLA, owns system accountability | Immediate triage |

---

## 6. Where RecoverAI Adds Value

| Step in Workflow | Value Added |
|:---|:---|
| Data submission | Data Quality Engine prevents impossible readings corrupting clinical decisions |
| Baseline computation | Patient-specific baseline prevents misclassification from population-level cutoffs |
| Trend analysis | Slope + persistence detection catches gradual multi-day deterioration |
| Alert decision | Multi-signal agreement requirement reduces 96.5% of low-value false alerts |
| Alert suppression | "Why No Alert?" transparency allows care teams to audit suppression decisions |
| Ownership | Named owner + SLA timer eliminates ownership gaps at shift transitions |
| Escalation | Automatic 3-tier escalation ensures no high-priority case can silently disappear |
| Monitoring gaps | Automatic detection of silent patients prevents dangerous false-stable assumptions |

---

## 7. System Does NOT Replace

- Physical clinical examination
- In-person wound assessment
- Clinical diagnostic judgement
- Emergency response (system is advisory, not autonomous)
- Medication prescribing decisions

All RecoverAI outputs are decision-support suggestions for human review.
