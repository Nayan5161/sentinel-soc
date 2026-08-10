from pymongo import MongoClient, ASCENDING

from .config import (
    MONGODB_URI,
    MONGODB_DATABASE,
    EVENTS_COLLECTION,
    SYSTEMS_COLLECTION,
    INCIDENTS_COLLECTION,
)

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000
)

db = client[MONGODB_DATABASE]

events = db[EVENTS_COLLECTION]
systems = db[SYSTEMS_COLLECTION]
incidents = db[INCIDENTS_COLLECTION]


def ping():
    return client.admin.command("ping")


def initialize_indexes():
    events.create_index(
        [("timestamp", ASCENDING)]
    )

    events.create_index(
        [("detection.suspicious", ASCENDING)]
    )

    events.create_index(
        [("event.severity", ASCENDING)]
    )

    events.create_index(
        [("source.source_id", ASCENDING)]
    )

    systems.create_index(
        [("system_id", ASCENDING)],
        unique=True
    )

    incidents.create_index(
        [("incident_id", ASCENDING)],
        unique=True
    )
