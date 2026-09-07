import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RecoverAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./recoverai.db"
    
    # Clinical Safety & Engine Thresholds
    TREND_SHORT_WINDOW: int = 3       # Observations for short-term rate of change
    TREND_MEDIUM_WINDOW: int = 7      # Observations for medium-term trajectory
    BASELINE_STABLE_WINDOW: int = 5   # Observations used to establish rolling baseline
    
    # Alert Suppression & Grouping
    ALERT_EPISODE_WINDOW_HOURS: int = 24  # Window within which alerts are grouped into an episode
    PERSISTENCE_MIN_READINGS: int = 2     # Minimum consecutive worsening readings required for High Priority
    
    # Task SLA & Escalation
    TASK_DUE_HOURS_HIGH: int = 2      # High Priority task SLA
    TASK_DUE_HOURS_REVIEW: int = 6    # Review priority task SLA
    TASK_DUE_HOURS_WATCH: int = 24    # Watch task SLA
    
    # Alert Reduction Target
    ALERT_REDUCTION_TARGET_PCT: float = 30.0

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
