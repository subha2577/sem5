import os
import sys
import uuid
import random
import argparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.services.data_quality_engine import DataQualityEngine

SURGERY_TYPES = [
    "Total Knee Arthroplasty",
    "Laparoscopic Cholecystectomy",
    "Colorectal Resection",
    "Coronary Artery Bypass",
    "Total Hip Replacement",
    "Spinal Lumbar Fusion",
    "Appendectomy"
]

AGE_GROUPS = ["18-35", "36-50", "51-65", "65+"]
CARE_TEAMS = ["Team Alpha", "Team Bravo", "Team Charlie", "Team Delta"]
CONTACT_METHODS = ["Mobile App", "SMS", "Phone Call"]

def generate_synthetic_dataset(num_patients: int = 1000, target_observations: int = 50000):
    """
    Generates realistic synthetic cohort spanning 10 clinical trajectories and 5 signature demo patients.
    """
    print(f"Generating synthetic dataset with {num_patients} patients and target {target_observations} observations...")
    
    random.seed(42)
    np.random.seed(42)

    patients = []
    observations = []

    # Calculate average observations per patient to reach target
    avg_obs = max(5, int(target_observations / num_patients))

    # Define Trajectory Groups
    groups = [
        ("Group A - Normal Recovery", 0.35, "no_action"),
        ("Group B - Temporary Variation", 0.20, "monitor"),
        ("Group C - Gradual Deterioration", 0.12, "review"),
        ("Group D - Wound-Dominant Deterioration", 0.08, "review"),
        ("Group E - Pain-Dominant Deterioration", 0.07, "review"),
        ("Group F - Multi-Signal Deterioration", 0.08, "urgent_review"),
        ("Group G - Missing Data", 0.04, "review"),
        ("Group H - Noisy Measurements", 0.03, "no_action"),
        ("Group I - Delayed Reporting", 0.01, "monitor"),
        ("Group J - Recovery After Intervention", 0.02, "review")
    ]
    group_names = [g[0] for g in groups]
    group_weights = [g[1] for g in groups]
    group_outcomes = {g[0]: g[2] for g in groups}

    # 1. Generate 5 Signature Demo Patients first
    demo_specs = [
        {
            "id": "REC-001",
            "group": "Group A - Normal Recovery",
            "surgery": "Total Knee Arthroplasty",
            "age": "51-65",
            "gt": "no_action",
            "risk_baseline": "Standard"
        },
        {
            "id": "REC-002",
            "group": "Group B - Temporary Variation",
            "surgery": "Laparoscopic Cholecystectomy",
            "age": "36-50",
            "gt": "monitor",
            "risk_baseline": "Standard"
        },
        {
            "id": "REC-003",
            "group": "Group C - Gradual Deterioration",
            "surgery": "Colorectal Resection",
            "age": "65+",
            "gt": "review",
            "risk_baseline": "Elevated"
        },
        {
            "id": "REC-004",
            "group": "Group F - Multi-Signal Deterioration",
            "surgery": "Coronary Artery Bypass",
            "age": "65+",
            "gt": "urgent_review",
            "risk_baseline": "Elevated"
        },
        {
            "id": "REC-005",
            "group": "Group G - Missing Data",
            "surgery": "Total Hip Replacement",
            "age": "51-65",
            "gt": "review",
            "risk_baseline": "Standard"
        }
    ]

    for p_idx in range(num_patients):
        if p_idx < len(demo_specs):
            spec = demo_specs[p_idx]
            p_id = spec["id"]
            p_group = spec["group"]
            surgery = spec["surgery"]
            age = spec["age"]
            gt_outcome = spec["gt"]
            risk_base = spec["risk_baseline"]
        else:
            p_id = f"PAT-{1000 + p_idx}"
            p_group = np.random.choice(group_names, p=group_weights)
            surgery = random.choice(SURGERY_TYPES)
            age = random.choice(AGE_GROUPS)
            gt_outcome = group_outcomes[p_group]
            risk_base = "Elevated" if "Deterioration" in p_group else "Standard"

        start_date = datetime.utcnow() - timedelta(days=random.randint(4, 10))
        care_team = random.choice(CARE_TEAMS)
        
        patient = {
            "patient_id": p_id,
            "age_group": age,
            "surgery_type": surgery,
            "surgery_date": start_date,
            "postoperative_day": random.randint(3, 8),
            "recovery_phase": "Early Post-Op",
            "baseline_risk_category": risk_base,
            "comorbidity_count": random.randint(0, 3) if risk_base == "Standard" else random.randint(2, 5),
            "preferred_contact_method": random.choice(CONTACT_METHODS),
            "assigned_care_team": care_team,
            "trajectory_group": p_group,
            "ground_truth_escalation": gt_outcome
        }
        patients.append(patient)

        # Generate observations for this patient
        num_obs_for_patient = avg_obs
        if p_group == "Group G - Missing Data":
            num_obs_for_patient = max(2, int(avg_obs * 0.4)) # Stops reporting early

        base_pain = round(random.uniform(2.5, 4.0), 1)
        base_temp = round(random.uniform(36.6, 37.0), 1)

        for step in range(num_obs_for_patient):
            obs_id = f"OBS-{uuid.uuid4().hex[:8].upper()}"
            obs_time = start_date + timedelta(hours=step * 12 + random.randint(-1, 1))
            post_op_day = min(10, 1 + int(step / 2))

            # Simulate vitals according to Trajectory Group
            quarantined = False
            quarantine_reason = None
            is_spike = False

            if p_group == "Group A - Normal Recovery":
                # Gradual improvement
                pain = max(0.5, base_pain - (step * 0.4) + random.uniform(-0.3, 0.3))
                temp = base_temp + random.uniform(-0.15, 0.15)
                redness = max(0.0, 1.5 - (step * 0.2))
                swelling = max(0.0, 1.5 - (step * 0.2))
                discharge = 0.0
                concern = "None"

            elif p_group == "Group B - Temporary Variation":
                # Isolated spike at step 3 or 4, then instant return
                if step == 3:
                    pain = base_pain + 3.5 # isolated spike
                    temp = 38.0
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.5
                    concern = "Mild"
                    is_spike = True
                elif step > 3:
                    # Returns to normal recovery
                    pain = max(1.0, base_pain - 0.5)
                    temp = base_temp + random.uniform(-0.1, 0.1)
                    redness = 0.5
                    swelling = 0.5
                    discharge = 0.0
                    concern = "None"
                else:
                    pain = base_pain + random.uniform(-0.2, 0.2)
                    temp = base_temp + random.uniform(-0.1, 0.1)
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"

            elif p_group == "Group C - Gradual Deterioration":
                # Progressive worsening across days
                if step <= 2:
                    pain = base_pain
                    temp = base_temp
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"
                else:
                    pain = min(9.5, base_pain + ((step - 2) * 1.2))
                    temp = min(39.2, base_temp + ((step - 2) * 0.4))
                    redness = min(4.5, 1.0 + ((step - 2) * 0.8))
                    swelling = min(4.0, 1.0 + ((step - 2) * 0.7))
                    discharge = min(3.5, (step - 2) * 0.6)
                    concern = "Moderate" if step < 5 else "Severe"

            elif p_group == "Group D - Wound-Dominant Deterioration":
                # Temp remains normal, wound deteriorates heavily
                temp = base_temp + random.uniform(-0.1, 0.1) # afebrile
                if step <= 2:
                    pain = base_pain
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"
                else:
                    pain = min(8.0, base_pain + ((step - 2) * 0.8))
                    redness = min(5.0, 1.5 + ((step - 2) * 1.0))
                    swelling = min(5.0, 1.5 + ((step - 2) * 0.9))
                    discharge = min(5.0, 0.5 + ((step - 2) * 1.1))
                    concern = "Moderate"

            elif p_group == "Group E - Pain-Dominant Deterioration":
                # Severe escalating pain without infection signs
                temp = base_temp + random.uniform(-0.1, 0.1)
                redness = 0.5
                swelling = 0.5
                discharge = 0.0
                if step <= 2:
                    pain = base_pain
                    concern = "None"
                else:
                    pain = min(10.0, base_pain + ((step - 2) * 1.6))
                    concern = "Severe"

            elif p_group == "Group F - Multi-Signal Deterioration":
                # Severe concurrent multi-system breakdown
                if step <= 2:
                    pain = base_pain
                    temp = base_temp
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"
                else:
                    pain = min(10.0, base_pain + ((step - 2) * 1.5))
                    temp = min(39.8, base_temp + ((step - 2) * 0.6))
                    redness = min(5.0, 1.5 + ((step - 2) * 1.0))
                    swelling = min(5.0, 1.5 + ((step - 2) * 0.9))
                    discharge = min(5.0, 1.0 + ((step - 2) * 1.0))
                    concern = "Severe"

            elif p_group == "Group H - Noisy Measurements":
                # Injected sensor error / impossible reading
                if step == 2:
                    pain = 14.0 # Impossible
                    temp = 44.2 # Impossible
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"
                    quarantined = True
                    quarantine_reason = "Critical invalid temperature: 44.2°C; Pain score 14.0 outside 0-10 scale"
                else:
                    pain = base_pain
                    temp = base_temp
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"

            elif p_group == "Group J - Recovery After Intervention":
                # Deteriorates at step 3-4, receives antibiotics/intervention, then recovers
                if step in [3, 4]:
                    pain = 7.5
                    temp = 38.3
                    redness = 3.5
                    swelling = 3.0
                    discharge = 2.0
                    concern = "Moderate"
                elif step > 4:
                    pain = max(1.5, 7.5 - ((step - 4) * 1.8))
                    temp = 36.9
                    redness = max(0.5, 3.5 - ((step - 4) * 1.0))
                    swelling = max(0.5, 3.0 - ((step - 4) * 0.8))
                    discharge = 0.0
                    concern = "Mild" if step == 5 else "None"
                else:
                    pain = base_pain
                    temp = base_temp
                    redness = 1.0
                    swelling = 1.0
                    discharge = 0.0
                    concern = "None"

            else:
                # Group G / I standard progression
                pain = max(1.0, base_pain - (step * 0.2))
                temp = base_temp
                redness = 1.0
                swelling = 1.0
                discharge = 0.0
                concern = "None"

            comp_wound = DataQualityEngine.calculate_composite_wound_score(
                round(redness, 1), round(swelling, 1), round(discharge, 1), round(min(5.0, pain / 2.0), 1)
            )

            obs = {
                "observation_id": obs_id,
                "patient_id": p_id,
                "timestamp": obs_time,
                "postoperative_day": post_op_day,
                "pain_score": round(pain, 1),
                "temperature": round(temp, 1),
                "wound_redness_score": round(redness, 1),
                "wound_swelling_score": round(swelling, 1),
                "wound_discharge_score": round(discharge, 1),
                "wound_pain_score": round(min(5.0, pain / 2.0), 1),
                "composite_wound_score": comp_wound,
                "fatigue_score": round(min(10.0, 2.0 + (pain * 0.6)), 1),
                "nausea_score": round(min(10.0, 1.0 if pain > 7 else 0.0), 1),
                "dizziness_score": 0.0,
                "mobility_score": round(max(1.0, 8.0 - (pain * 0.7)), 1),
                "appetite_score": round(max(2.0, 8.0 - (pain * 0.5)), 1),
                "patient_reported_concern": concern,
                "medication_adherence": "Full",
                "sleep_quality": round(max(1.0, 8.0 - (pain * 0.6)), 1),
                "data_source": "Mobile App",
                "measurement_quality": "Poor" if quarantined else ("Fair" if is_spike else "Good"),
                "is_quarantined": quarantined,
                "quarantine_reason": quarantine_reason
            }
            observations.append(obs)

    # Save to data directories
    os.makedirs("data/synthetic", exist_ok=True)
    df_patients = pd.DataFrame(patients)
    df_obs = pd.DataFrame(observations)

    df_patients.to_csv("data/synthetic/patients.csv", index=False)
    df_obs.to_csv("data/synthetic/observations.csv", index=False)

    print(f"Generated {len(patients)} patients and {len(observations)} observations.")
    print("Files saved to data/synthetic/patients.csv and data/synthetic/observations.csv")
    return df_patients, df_obs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic post-op patient dataset")
    parser.add_argument("--patients", type=int, default=1000, help="Number of patients (default: 1000)")
    parser.add_argument("--observations", type=int, default=50000, help="Target observation count (default: 50000)")
    args = parser.parse_args()

    generate_synthetic_dataset(num_patients=args.patients, target_observations=args.observations)
