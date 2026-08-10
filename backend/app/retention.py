from .db import events
from .config import RETENTION_HARD_MB, RETENTION_TARGET_MB


def get_collection_size_mb():
    stats = events.database.command(
        "collStats",
        events.name
    )

    return stats.get("size", 0) / (
        1024 * 1024
    )


def enforce_retention():
    current_mb = get_collection_size_mb()

    if current_mb <= RETENTION_HARD_MB:
        return {
            "action": "none",
            "before_mb": round(current_mb, 3),
            "after_mb": round(current_mb, 3),
            "deleted": 0
        }

    target_bytes = (
        RETENTION_TARGET_MB
        * 1024
        * 1024
    )

    deleted = 0

    cursor = events.find(
        {},
        {
            "_id": 1
        }
    ).sort(
        "timestamp",
        1
    )

    for document in cursor:
        current_mb = get_collection_size_mb()

        if current_mb <= RETENTION_TARGET_MB:
            break

        events.delete_one({
            "_id": document["_id"]
        })

        deleted += 1

    after_mb = get_collection_size_mb()

    return {
        "action": "cleanup",
        "before_mb": round(
            current_mb,
            3
        ),
        "after_mb": round(
            after_mb,
            3
        ),
        "deleted": deleted
    }
