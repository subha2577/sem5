# RecoverAI — Stakeholder / Prototype Walkthrough Validation

> **IMPORTANT DISCLAIMER**: No real clinical stakeholder participated in this validation. This document records a structured prototype walkthrough conducted as part of academic evaluation. It is clearly labelled as a simulated walkthrough, not a real clinical validation study.
>
> This prototype demonstrates a concept. It does not claim clinical approval, clinician endorsement, or regulatory certification.

---

## 1. Purpose

The project brief requires a short user/stakeholder validation. Because no real hospital staff or patients are available for this academic prototype, this document records a structured walkthrough using three synthetic reviewer personas that represent the primary care team roles the system is designed for.

Each reviewer persona was defined before the walkthrough. Scenarios were demonstrated against the live prototype. Observations were recorded honestly.

---

## 2. Reviewer Personas

| Persona | Role | Clinical Context |
|:---|:---|:---|
| **Persona A** | Nurse Reviewer | Primary user of the Priority Queue and patient detail view. Responsible for reviewing High Priority alerts within 2h SLA. |
| **Persona B** | Care Coordinator | Monitors Watch/Review-category patients. Manages follow-up tasks and monitoring gaps. |
| **Persona C** | Clinical Supervisor | Receives escalated overdue tasks. Needs rapid situational overview and escalation chain visibility. |

---

## 3. Scenarios Demonstrated

### Scenario 1 — Stable Recovery Patient (REC-001)
- **Shown to**: All personas
- **What was demonstrated**: Patient with gradual improvement. Risk score 14/100. Stable trajectory. No alert generated. Overview dashboard shows patient in low-priority zone.
- **Observed feedback (Persona A)**: "This is what I expect to see for a straightforward recovery. The 14/100 score is reassuring — it is explicit. Better than just a green dot."
- **Observed feedback (Persona B)**: "I like that I can see the trend direction, not just a single number."
- **Usability issue noted**: The baseline deviation numbers are visible but require clinical numeracy to interpret. A simpler qualitative label ("Within expected range") alongside the number would help.

### Scenario 2 — Isolated Transient Spike (REC-002)
- **Shown to**: Persona A, Persona C
- **What was demonstrated**: Patient with pain=6.5 and temp=38.0 on day 3, returning to baseline by day 4. Alert suppressed. "Why No Alert?" card visible.
- **Observed feedback (Persona A)**: "This is exactly the kind of thing that floods our inbox with the current system. The fact that it explains WHY it did not alert is more valuable than the alert itself."
- **Observed feedback (Persona C)**: "I need to trust that the system is not hiding things. The explicit suppression reason gives me that confidence."
- **Usability issue noted**: The suppression card could be more prominent. It was missed initially. Suggested: highlight suppression events in a dedicated "Reviewed and Suppressed" log.

### Scenario 3 — Multi-Signal Deterioration (REC-004)
- **Shown to**: Persona A, Persona B
- **What was demonstrated**: Patient with concurrent pain, fever, wound deterioration across days 5-8. Risk 88/100 High Priority. "What Changed?" panel visible. Escalation task with 2h SLA and owner assigned.
- **Observed feedback (Persona A)**: "The bullet point explanation in the What Changed panel is what I would write in a handoff note anyway. This saves me cognitive effort."
- **Observed feedback (Persona B)**: "Having the owner and due time visible means I know it is being handled. That is the escalation gap we have in our current system."
- **Usability issue noted**: Font size on the risk contributor breakdown chart is small on a 13-inch laptop screen.

### Scenario 4 — Monitoring Gap (REC-005)
- **Shown to**: Persona C, Persona B
- **What was demonstrated**: Patient stopped reporting on day 4. Monitoring gap flagged. Follow-up task created with Care Coordinator assigned and 6h SLA.
- **Observed feedback (Persona C)**: "Monitoring gaps are our biggest blind spot. A patient who goes quiet is our highest concern — not the one who keeps sending readings."
- **Observed feedback (Persona B)**: "The task appears automatically. In our current workflow, spotting a gap relies on me manually checking every patient file."
- **Usability issue noted**: Would benefit from a phone-number or contact-method quick link on the monitoring gap card.

### Scenario 5 — Overdue Escalation
- **Shown to**: Persona C
- **What was demonstrated**: Task overdue by 1h. Escalation level advanced to Level 2 (Clinical Supervisor). OVERDUE badge visible. "Check Overdue Escalations" triggered live.
- **Observed feedback (Persona C)**: "The Level 3 Operations Queue concept is exactly what we would need. The escalation chain matching our real governance structure is important."
- **Usability issue noted**: Would prefer a push notification (email/SMS) to be sent on Level 2 escalation, not only a dashboard badge.

---

## 4. Summary of Feedback

| Area | Positive | Concern |
|:---|:---|:---|
| Alert reduction | "Why No Alert?" panel highly valued | Suppression card visibility needs improvement |
| Explainability | "What Changed?" bullet points appreciated | Numeric deviations require clinical numeracy |
| Escalation chain | Three-tier escalation matches real workflows | Push notifications missing (email/SMS) |
| Monitoring gaps | Automatic detection highly valued | Contact method quick link missing |
| Risk score | Explicit numeric score + category appreciated | Small contributor chart text on small screens |

---

## 5. Changes Made Based on Walkthrough Observations

The following changes were considered based on walkthrough feedback:

| Feedback Item | Action Taken |
|:---|:---|
| Suppression card visibility | Alert engine includes is_suppressed=True records in separate suppressed log accessible from UI |
| Qualitative baseline label | risk_engine.py generates "Within expected range" / "Elevated above baseline" narrative in what_changed_summary |
| Escalation structure matches real workflow | Confirmed: escalation_engine.py implements Nurse → Supervisor → Operations Queue matching persona workflows |
| Push notifications | Out of scope for prototype; documented as implementation requirement for production deployment |
| Contact method link | patient_reported_concern and preferred_contact_method fields available in Patient entity; UI enhancement documented for future sprint |

---

## 6. Limitations of This Validation

1. All reviewer personas are synthetic — no real nurse, coordinator, or supervisor participated.
2. Feedback is inferred from domain knowledge of clinical workflows, not recorded from real people.
3. This constitutes a structured prototype self-review, not a user study.
4. Real clinical usability testing would require IRB/ethics approval, trained clinical participants, and a structured usability protocol (e.g. think-aloud method, SUS score).
5. No clinical accuracy or safety conclusion is implied by this walkthrough.

---

## 7. Conclusion

The structured prototype walkthrough suggests that the core differentiators of RecoverAI — "Why No Alert?" suppression transparency, patient-specific baselines, automatic monitoring gap detection, and three-tier escalation — align with identified operational pain points in post-operative remote monitoring workflows.

Real stakeholder validation is required before any deployment consideration. This walkthrough demonstrates prototype readiness for academic evaluation only.
