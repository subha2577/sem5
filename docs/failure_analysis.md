# RecoverAI: Failure Mode & Error Analysis

## 1. Comprehensive Failure Modes Matrix

| Failure Mode | Root Cause | Clinical / System Impact | Detection Mechanism | Mitigation Strategy | Residual Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Missing Data / Inactive Patient** | Patient stops reporting home observations | Deterioration or complications go unmonitored | `MONITORING_GAP` flag raised when elapsed time > 36h | Spawns automated phone/SMS outreach task for Care Coordinator | Patient unreachable by telephone |
| **2. Duplicate Submissions** | Network retry storm or accidental multi-tap | Skews rolling baseline and inflates persistence | `DUPLICATE_ENTRY` check matches identical timestamps | Second entry quarantined; alert generation blocked | High-frequency valid rapid telemetry within seconds |
| **3. Impossible Physiological Readings** | Sensor detachment, data corruption, typo (e.g. 44.5°C) | Triggers false emergency alerts or corrupts trend | Range validator: Temp $\notin [34.0, 42.5]^\circ$C or Pain $\notin [0, 10]$ | Reading isolated to quarantine table; patient prompted to re-measure | Subtle borderline invalid values (e.g. 39.9°C typo from 36.9°C) |
| **4. Sudden Measurement Spike** | Transient acute discomfort (e.g. post-PT) | Alarm fatigue from single non-sustained reading | `SUDDEN_JUMP` flag + persistence requirement ($\ge 2$) | Suppressed as "Watch / Isolated Spike" with "Why No Alert?" card | Very rapid acute deterioration requiring immediate check |
| **5. Conflicting Signals** | Pain decreases due to analgesia, but wound erythema worsens | Missed infection masked by systemic pain relief | Multi-signal divergence check (`agreeing_signals` count) | Flagged as "Mixed Recovery Signals" requiring visual wound photo review | Subjective interpretation bias by reviewer |
| **6. Unresolved High-Priority Task** | Care team unavailable or shift change gap | Deteriorating patient left without timely intervention | Cron / API SLA scanner checks `now > task.due_at` | Auto-escalation: Level 1 (Nurse) $\to$ Level 2 (Supervisor) $\to$ Level 3 (Ops) | Widespread staffing shortage across all tiers |
| **7. Backend / API Outage** | Process failure, network disconnection | Frontend cannot fetch telemetry or risk scores | Global HTTP middleware + frontend fallback handlers | Displays non-blocking clinical banner with cached state and retry options | Telemetry delays during extended network blackout |
| **8. Empty Dataset Initialization** | Fresh installation or cleared database | Blank white screens or crash in UI components | Empty state guards on tables and Recharts canvases | Renders clear clinical onboarding guide with "Seed Demo Cohort" CTA | New facility confusion during day-1 deployment |
| **9. Delayed Submissions** | Patient uploads 3 days of backlogged readings at once | Distorts rolling baseline timing assumptions | Submission timestamp vs observation timestamp delta check | Re-orders telemetry chronologically before computing slopes | Temporal compression can mimic sudden rate-of-change jumps |
| **10. Contradictory Patient Reporting** | Patient reports pain = 0 but marks severe purulent discharge | Misleads simple rule engines | `CONTRADICTORY_SIGNALS` rule checks discordance | Telemetry quality deducted by 15 pts; flags clinical review | Communication barrier or cognitive impairment |
| **11. Sensor Noise / Drift** | Smart thermometer calibration drift over weeks | Subtle artificial drift in baseline temperature | Longitudinal variance standard deviation bound ($\sigma$) | Recalculates rolling median to dampen outlier drift | Slow, uniform calibration drift |
| **12. Human Reviewer Error** | Reviewer mistakenly resolves task without contacting patient | Deterioration escalates post-discharge | Audit trail requires mandatory clinical resolution note | Peer review audit sampling by Clinical Supervisor | Erroneous clinical judgement by credentialed provider |

---

## 2. Testing & Verification of Failure Guardrails
All critical failure modes are covered by the automated Pytest suite in `backend/tests/test_data_quality.py`, `backend/tests/test_alert_engine.py`, and `backend/tests/test_escalation_engine.py`:
- `test_critical_temperature_quarantine()`: Verified quarantine on 43.5°C input.
- `test_duplicate_timestamp_quarantine()`: Verified duplicate quarantine.
- `test_sudden_jump_detection()`: Verified jump dampening.
- `test_overdue_task_auto_escalation_level_2()`: Verified Level 1 $\to$ Level 2 supervisory handoff.
- `test_overdue_task_auto_escalation_level_3()`: Verified Level 2 $\to$ Level 3 escalation queue.
