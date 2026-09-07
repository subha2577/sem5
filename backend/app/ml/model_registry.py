import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "saved_models", "registry.json")

class ModelRegistry:
    """Tracks model versions, deployment dates, and active status."""

    @classmethod
    def register_model(
        cls,
        version_tag: str,
        metrics: Dict[str, Any],
        feature_importance: Dict[str, float],
        is_active: bool = True
    ) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
        
        entry = {
            "model_name": "trend-risk-classifier",
            "version_tag": version_tag,
            "trained_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "feature_importance": feature_importance,
            "is_active": is_active
        }

        registry = cls.get_all_versions()
        # Mark others inactive if this is active
        if is_active:
            for item in registry:
                item["is_active"] = False
        registry.append(entry)

        with open(REGISTRY_FILE, "w") as f:
            json.dump(registry, f, indent=2)

        return entry

    @classmethod
    def get_all_versions(cls) -> list:
        if not os.path.exists(REGISTRY_FILE):
            return []
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def get_active_model(cls) -> Optional[Dict[str, Any]]:
        versions = cls.get_all_versions()
        for v in reversed(versions):
            if v.get("is_active", True):
                return v
        return versions[-1] if versions else None
