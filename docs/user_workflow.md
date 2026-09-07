# RecoverAI: Clinical Operations & User Workflow

## 1. End-to-End Operational Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Patient as Patient (Home RPM)
    participant DQ as Data Quality Engine
    participant PB as Baseline & Trend Engine
    participant Risk as Risk & Alert Engine
    participant Task as Task Escalation Service
    actor Nurse as Nurse Reviewer
    actor Sup as Clinical Supervisor

    Patient->>DQ: Submits Observation (Pain, Temp, Wound, Fatigue)
    DQ->>DQ: Validates physiological ranges & checks sudden jumps
    alt Physiologically Impossible Reading
        DQ-->>Patient: Flags & quarantines measurement without drop
    else Valid Telemetry
        DQ->>PB: Ingest valid observation
        PB->>PB: Computes rolling delta from personal baseline (Δ)
        PB->>PB: Computes short & medium trajectory slopes
        PB->>Risk: Evaluates persistence & multi-signal agreement
        Risk->>Risk: Derives composite Risk Score (0-100)
        alt Isolated Transient Spike (Watch)
            Risk->>Risk: Suppress alert from main queue ("Why No Alert?" card generated)
        else Multi-Signal / Persistent Deterioration (Review / High Priority)
            Risk->>Risk: Deduplicate into active Alert Episode
            Risk->>Task: Create clinical follow-up task
            Task->>Nurse: Assign ownership with strict SLA timer
            alt Nurse completes review within SLA
                Nurse->>Task: Enters resolution note & resolves task
            else SLA Expires (Overdue)
                Task->>Sup: Auto-escalate to Level 2 (Clinical Supervisor)
                Sup->>Patient: Intervene or triage to acute care
            end
        end
    end
```

---

## 2. Care Team Personas & Responsibilities

| Role | Synthetic Owner Name | Primary Dashboard Views | SLA Responsibilities |
| :--- | :--- | :--- | :--- |
| **Care Coordinator** | Coordinator Alex | Overview, Priority Queue | Monitors early recovery patients, reviews Watch/Review items within 6 hours |
| **Nurse Reviewer** | Nurse Sarah | Priority Queue, Patient Timeline | Investigates High Priority alerts, reviews "What Changed?" summary within 2 hours |
| **Clinical Supervisor** | Dr. Miller | Tasks & Escalation Queue | Receives Level 2 auto-escalated overdue tasks, directs clinical interventions |
| **Escalation Manager** | Operations Queue | System Health, Audit Trail | Manages Level 3 system bottlenecks and care pathway exceptions |
