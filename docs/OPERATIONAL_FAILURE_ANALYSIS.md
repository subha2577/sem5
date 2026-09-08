# RecoverAI — Operational Failure Mode Analysis

> **SAFETY NOTICE**: This prototype is a clinical decision-support tool only. It does not replace clinical judgement. All outputs require review by qualified healthcare professionals. No autonomous medical diagnosis, treatment, or emergency response is provided or implied.

---

## 1. Purpose

This document explicitly catalogues how RecoverAI can fail in real clinical operations. Transparent documentation of failure modes is a prerequisite for responsible deployment of any clinical decision-support prototype.

**Key Principle**: RecoverAI prioritises observations for human review. A human clinician must always be the final decision-maker.

---

## 2. Comprehensive Operational Failure Mode Table

| # | Failure Mode | What Can Go Wrong | Operational Impact | Detection Mechanism | Mitigation Strategy | Human Responsibility |
|:--|:---|:---|:---|:---|:---|:---|
| 1 | **Missing Patient Observations** | Patient stops submitting home readings | Deterioration goes unmonitored | MONITORING_GAP flag raised after 36h | Spawns automated outreach task with SLA | Care Coordinator contacts patient; Supervisor authorises home visit |
| 2 | **Physiologically Impossible Readings** | Impossible temperature/pain values | Corrupts baseline or false alert | Range validation: Temp not in [34,42.5], Pain not in [0,10] triggers quarantine | Observation quarantined; no alert generated from quarantined record | Clinician reviews quarantine log; IT verifies device calibration |
| 3 | **Insufficient Baseline History** | New patient with fewer than 3 observations | Deviation calculations unreliable | baseline_uncertain flag in BaselineEngine | Conservative confidence flagging; population defaults applied conservatively | Reviewer manually assesses new patients with fewer than 3 observations |
| 4 | **False Positive Alert** | Isolated transient spike (post-physiotherapy pain) triggers escalation | Alert fatigue erodes clinical trust | persistence_count < 2 AND no multi-signal agreement = Watch, not escalated | Isolated spikes suppressed; Why No Alert card generated | Clinical governance reviews suppression configuration periodically |
| 5 | **False Negative (Missed Deterioration)** | Slow low-amplitude deterioration below detection thresholds | Patient deteriorates without intervention | 7-day medium-term slope designed to detect gradual change | Minimum recall target 88% enforced in evaluation | Clinical Supervisor periodically reviews all Watch-category patients |
| 6 | **Transient Abnormality Misclassified** | Single reading resolves next day but still triggers alert | Clinician contacted unnecessarily | Persistence counter requires 2 consecutive worsening readings | Why No Alert panel explains suppression | Care Coordinator monitors Watch patients without escalation action |
| 7 | **Delayed Data Submission** | Patient submits 3 days of backlogged readings simultaneously | Distorts baseline timing; mimics sudden rate-of-change | Submission vs observation timestamp delta check | Telemetry re-ordered chronologically; flagged as monitoring gap | Reviewer interprets timeline with awareness of delay flag |
| 8 | **Duplicate Submissions** | Network retry causes identical observation twice | Skews baseline and persistence counter | DUPLICATE_ENTRY flag matches identical patient+timestamp | Second duplicate quarantined; alert generation blocked | IT reviews retry logic; patient educated on app usage |
| 9 | **Contradictory Signals** | Pain=0 but wound discharge=4 (analgesia masking infection) | Single-signal systems miss wound deterioration | CONTRADICTORY_SIGNALS rule: pain discordant with wound severity | Multi-signal analysis; Mixed Recovery Signals episode type | Nurse Reviewer confirms wound state physically or via photograph |
| 10 | **Alert Overload / Misconfiguration** | Thresholds set incorrectly causing alert flood | Care team overwhelmed; alert fatigue returns | Evaluation benchmark: Alert Reduction % monitored. Target >30%. | Threshold configuration in config.py; evaluation re-run after any change | Clinical governance owns threshold configuration |
| 11 | **API / Backend System Failure** | Backend crashes or database connection drops | Frontend blank; real-time monitoring ceases | Global HTTP middleware; health check at /api/health | Non-blocking clinical banner displayed; cached state shown; retry logic | IT on-call responds within SLA; Supervisor assumes manual monitoring during outage |
| 12 | **Missing Task Owner** | No nurse/coordinator assigned to care team | High-priority alert remains unreviewed | assigned_owner validated at task creation; Unassigned = immediate warning | Unassigned high-priority tasks escalate to Supervisor immediately | Clinical Operations Manager ensures all patients have assigned care team |
| 13 | **Overdue Follow-up / Escalation Failure** | Nurse does not review task within SLA | Patient in deterioration receives no contact | check_and_escalate_overdue_tasks scans active tasks; now > due_at = Overdue | Level 1 to Level 2 to Level 3 escalation; Overdue badge prominent in UI; cannot be silently dismissed | Escalation Manager owns Level 3 queue; Supervisor enforces policy |
| 14 | **Human Reviewer Error** | Reviewer resolves task without contacting patient | Deterioration continues; false resolution in audit trail | Mandatory resolution note required before closure; audit log records all actions | Peer review audit sampling by Clinical Supervisor | Supervisor conducts random audits; medical director owns accountability |

---

## 3. Three Mandatory Edge / Failure Cases (Tested)

### Edge Case 1 — Missing Data / Monitoring Gap
- **Scenario**: Patient REC-005 (Group G) stops reporting after day 4.
- **Expected System Behaviour**: MONITORING_GAP flag raised. has_monitoring_gap = True on Patient. Follow-up task created with owner and due date. Escalated to Clinical Supervisor if no resolution within 6h SLA.
- **Actual Behaviour (Verified)**: test_overdue_task_auto_escalation_level_2 and test_overdue_task_auto_escalation_level_3 pass. DataQualityEngine raises MONITORING_GAP when elapsed > 36h.
- **Why This Matters**: Prevents system from falsely assuming a silent patient is stable.

### Edge Case 2 — Invalid / Impossible Data
- **Scenario**: Patient in Group H submits temperature 44.2 degrees Celsius and pain score 14.0.
- **Expected System Behaviour**: Observation quarantined. No clinical alert generated. Patient prompted to re-measure. Quarantine logged to data_quality_events.
- **Actual Behaviour (Verified)**: test_critical_temperature_quarantine PASSED. test_invalid_pain_range_quarantine PASSED. DataQualityEngine validates all ranges.
- **Why This Matters**: Physiologically impossible readings must not trigger false clinical emergencies.

### Edge Case 3 — Transient Abnormality (Isolated Spike)
- **Scenario**: Patient REC-002 (Group B) has pain=6.5, temp=38.0 at step 3, returns to normal at step 4+.
- **Expected System Behaviour**: Alert suppressed from main queue (Watch only). Why No Alert card generated. No escalation task created.
- **Actual Behaviour (Verified)**: test_isolated_spike_suppressed PASSED. AlertEngine suppresses when persistence_count < 2 AND no multi-signal agreement.
- **Why This Matters**: This is the core clinical differentiator — individual abnormal readings must NOT automatically become high-priority alerts.

---

## 4. Prototype Limitations

1. **Synthetic data only** — All evaluation metrics come from synthetic cohort, not real patients.
2. **No real clinical validation** — No clinician has reviewed outputs in operational setting.
3. **Threshold sensitivity** — Alert reduction depends on configured persistence and slope thresholds.
4. **New patient baseline uncertainty** — Patients with fewer than 3 observations receive conservative population-level defaults.
5. **No physical assessment** — Cannot see wound photographs or assess in-person clinical signs.
6. **Human dependency** — Safety guarantees depend on human reviewers responding within SLAs.
7. **No regulatory approval** — Not a certified medical device; requires MHRA/FDA review for real deployment.

---

## 5. Safety Declaration

> **This prototype demonstrates a concept for clinical decision-support only.**
>
> It does not provide autonomous medical diagnosis, treatment recommendations, or emergency response.
>
> All outputs require review by qualified healthcare professionals.
>
> This synthetic evaluation suggests potential for alert fatigue reduction. Real-world clinical validation is required before any deployment consideration.
