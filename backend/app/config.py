import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "security_monitor"
)

EVENTS_COLLECTION = "events"
SYSTEMS_COLLECTION = "systems"
INCIDENTS_COLLECTION = "incidents"

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

RETENTION_HARD_MB = int(
    os.getenv("RETENTION_HARD_MB", "100")
)

RETENTION_TARGET_MB = int(
    os.getenv("RETENTION_TARGET_MB", "90")
)

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is not configured"
    )
