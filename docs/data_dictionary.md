# RecoverAI: Data Dictionary

## 1. Patient Entity (`patients` table)

| Field Name | Type | Description | Values / Constraints |
| :--- | :--- | :--- | :--- |
| `patient_id` | String(64) | Unique synthetic identifier | e.g. `REC-001`, `PAT-1042` |
| `age_group` | String(32) | Age category | `18-35`, `36-50`, `51-65`, `65+` |
| `surgery_type` | String(64) | Surgical procedure performed | e.g. `Total Knee Arthroplasty`, `Colorectal Resection` |
| `surgery_date` | DateTime | Timestamp of surgical procedure | ISO 8601 |
| `postoperative_day` | Integer | Post-operative day count (POD) | 1 to 30 |
| `recovery_phase` | String(32) | Current clinical recovery phase | `Early Post-Op`, `Transition`, `Late Recovery` |
| `baseline_risk_category`| String(32) | Baseline surgical risk stratification | `Standard`, `Elevated` |
| `comorbidity_count` | Integer | Number of pre-existing comorbidities | 0 to 5 |
| `preferred_contact_method`| String(32)| Preferred patient channel | `Mobile App`, `SMS`, `Phone Call` |
| `assigned_care_team` | String(64) | Primary clinical team | `Team Alpha`, `Team Bravo`, etc. |
| `current_risk_score` | Float | Latest computed composite risk | 0.0 to 100.0 |
| `current_priority` | String(32) | Current triage classification | `Stable`, `Watch`, `Review`, `High Priority` |
| `current_trend_direction`| String(32)| Trajectory trend direction | `Improving`, `Stable`, `Worsening`, `Mixed` |
| `latest_data_quality_score`| Float | Telemetry quality score | 0.0 to 100.0 |
| `primary_signal` | String(64) | Primary clinical driver of priority | e.g. `Multi-Signal Concurrent Deterioration` |
| `assigned_owner` | String(64) | Care team member responsible | e.g. `Nurse Sarah (Team Alpha)` |
| `has_monitoring_gap` | Boolean | True if elapsed time > 36 hours | `True`, `False` |
| `has_active_escalation` | Boolean | True if escalated to supervisor | `True`, `False` |

---

## 2. Observation Entity (`observations` table)

| Field Name | Type | Description | Valid Physiological Range |
| :--- | :--- | :--- | :--- |
| `observation_id` | String(64) | Unique reading identifier | e.g. `OBS-9D72E1A8` |
| `patient_id` | String(64) | Foreign key to `patients` | Indexed |
| `timestamp` | DateTime | Submission timestamp | UTC |
| `postoperative_day` | Integer | Post-op day at time of reading | $\ge 1$ |
| `pain_score` | Float | Visual analog scale pain score | 0.0 to 10.0 |
| `temperature` | Float | Body temperature in Celsius | 34.0°C to 42.5°C |
| `wound_redness_score` | Float | Surgical site erythema | 0.0 to 5.0 |
| `wound_swelling_score`| Float | Surgical site edema | 0.0 to 5.0 |
| `wound_discharge_score`| Float | Surgical site purulent drainage | 0.0 to 5.0 |
| `wound_pain_score` | Float | Localized incision pain | 0.0 to 5.0 |
| `composite_wound_score`| Float | Normalized composite wound index | 0.0 to 10.0 |
| `fatigue_score` | Float | Subjective systemic fatigue | 0.0 to 10.0 |
| `nausea_score` | Float | Gastrointestinal distress | 0.0 to 10.0 |
| `dizziness_score` | Float | Orthostatic or subjective dizziness | 0.0 to 10.0 |
| `mobility_score` | Float | Functional ambulation score | 0.0 to 10.0 (higher is better) |
| `appetite_score` | Float | Oral intake rating | 0.0 to 10.0 (higher is better) |
| `patient_reported_concern`| String(64)| Subjective patient concern | `None`, `Mild`, `Moderate`, `Severe` |
| `medication_adherence`| String(32) | Prescribed medication compliance | `Full`, `Missed Dose`, `Stopped` |
| `sleep_quality` | Float | Rest quality index | 0.0 to 10.0 |
| `data_source` | String(32) | Ingestion channel | `Mobile App`, `Smart Patch`, `Manual Entry` |
| `measurement_quality`| String(32) | Telemetry quality assessment | `Good`, `Fair`, `Poor` |
| `is_quarantined` | Boolean | Quarantined due to violation | `True`, `False` |
| `quarantine_reason` | String(256)| Specific physiological failure | Nullable |

---

## 3. Clinical Task Entity (`tasks` table)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `task_id` | String(64) | Unique clinical action identifier (`TSK-...`) |
| `patient_id` | String(64) | Associated patient |
| `alert_id` | String(64) | Associated trigger alert |
| `priority` | String(32) | `High Priority`, `Review`, `Watch` |
| `assigned_to` | String(64) | Designated clinician (e.g. `Nurse Sarah`) |
| `assigned_role` | String(64) | Role (`Nurse Reviewer`, `Clinical Supervisor`) |
| `created_at` | DateTime | Task creation timestamp |
| `due_at` | DateTime | Strict SLA expiration timestamp |
| `status` | String(32) | `New`, `Assigned`, `In Review`, `Resolved`, `Escalated` |
| `escalation_level`| Integer | `1` (Team), `2` (Supervisor), `3` (Escalation Queue) |
| `resolution_note` | Text | Clinical note documenting resolution rationale |
| `resolved_at` | DateTime | Completion timestamp |
