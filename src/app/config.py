
import os
from dataclasses import dataclass

@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "cfdp-stub")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # Proba d'envoyer un ACK (entre 0 et 1)
    ACK_PROBABILITY: float = float(os.getenv("ACK_PROBABILITY", "0.85"))

settings = Settings()
