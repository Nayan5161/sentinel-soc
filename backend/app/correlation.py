from datetime import datetime, timezone, timedelta
from uuid import uuid4

from .db import events, incidents


AUTH_ACTIONS = {
    "login_attempt",
    "login_failed",
    "failed_login",
    "authentication",
    "authentication_failure",
    "auth_failure",
    "ssh_login_failed",
}


def utc_now():
    return datetime.now(timezone.utc)


def create_incident(
    incident_type,
    title,
    severity,
    risk_score,
    confidence,
    explanation,
    recommendation,
    related_events,
    source_ip=None,
    username=None,
):
    """
    Create one incident document.

    Existing incidents are reused when the same type,
    source IP, and username are already active.
    """

    existing = incidents.find_one({
        "type": incident_type,
        "source_ip": source_ip,
        "username": username,
        "status": {
            "$in": [
                "open",
                "investigating"
            ]
        }
    })

    if existing:
        incidents.update_one(
            {
                "_id": existing["_id"]
            },
            {
                "$set": {
                    "updated_at": utc_now(),
                    "severity": severity,
                    "risk_score": risk_score,
                    "confidence": confidence,
                    "explanation": explanation,
                    "recommendation": recommendation,
                    "event_count": len(related_events),
                },
                "$addToSet": {
                    "related_event_ids": {
                        "$each": related_events
                    }
                }
            }
        )

        return incidents.find_one({
            "_id": existing["_id"]
        })

    incident = {
        "incident_id": str(uuid4()),
        "type": incident_type,
        "title": title,
        "status": "open",
        "severity": severity,
        "risk_score": risk_score,
        "confidence": confidence,
        "source_ip": source_ip,
        "username": username,
        "event_count": len(related_events),
        "related_event_ids": related_events,
        "explanation": explanation,
        "recommendation": recommendation,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    incidents.insert_one(incident)

    return incident


def correlate_event(event):
    """
    Check whether an event forms part of a larger incident.

    Returns:
        incident document or None
    """

    analysis = event.get(
        "analysis",
        {}
    )

    if not analysis.get("suspicious"):
        return None

    timestamp = event.get(
        "timestamp"
    )

    if not isinstance(timestamp, datetime):
        timestamp = utc_now()

    window_start = timestamp - timedelta(
        minutes=10
    )

    actor = event.get(
        "actor",
        {}
    )

    source_ip = actor.get(
        "ip"
    )

    username = actor.get(
        "user"
    )

    details = event.get(
        "event",
        {}
    )

    action = str(
        details.get(
            "action",
            ""
        )
    ).lower()

    category = str(
        details.get(
            "category",
            ""
        )
    ).lower()

    current_event_id = event.get(
        "event_id"
    )

    # ---------------------------------------------------------
    # Authentication correlation
    # ---------------------------------------------------------

    if (
        action in AUTH_ACTIONS
        and str(
            details.get(
                "status",
                ""
            )
        ).lower()
        in {
            "failed",
            "failure",
            "denied",
            "rejected"
        }
    ):

        query = {
            "timestamp": {
                "$gte": window_start,
                "$lte": timestamp
            },
            "actor.ip": source_ip,
            "actor.user": username,
            "event.action": {
                "$in": list(
                    AUTH_ACTIONS
                )
            },
            "event.status": {
                "$in": [
                    "failed",
                    "failure",
                    "denied",
                    "rejected"
                ]
            }
        }

        related = list(
            events.find(
                query,
                {
                    "event_id": 1,
                    "analysis": 1,
                    "timestamp": 1
                }
            )
        )

        if len(related) >= 5:

            event_ids = [
                item.get(
                    "event_id"
                )
                for item in related
                if item.get("event_id")
            ]

            if current_event_id:
                event_ids.append(
                    current_event_id
                )

            return create_incident(
                incident_type="authentication_bruteforce",
                title="Possible Brute-Force Attack",
                severity="CRITICAL",
                risk_score=91,
                confidence=0.94,
                source_ip=source_ip,
                username=username,
                related_events=list(
                    set(event_ids)
                ),
                explanation=(
                    f"{len(set(event_ids))} failed authentication "
                    "attempts were detected from the same source "
                    "against the same account within a short time window."
                ),
                recommendation=(
                    "Investigate the source IP, verify the account "
                    "owner, review authentication logs, and consider "
                    "temporary containment if the activity is unauthorized."
                ),
            )

    # ---------------------------------------------------------
    # Suspicious web activity
    # ---------------------------------------------------------

    if (
        category in {
            "web",
            "http",
            "application"
        }
        and analysis.get(
            "rule_id"
        ) == "WEB-001"
    ):

        query = {
            "timestamp": {
                "$gte": window_start,
                "$lte": timestamp
            },
            "actor.ip": source_ip,
            "detection.rule_id": "WEB-001"
        }

        related = list(
            events.find(
                query,
                {
                    "event_id": 1,
                    "timestamp": 1
                }
            )
        )

        if len(related) >= 3:

            event_ids = [
                item.get(
                    "event_id"
                )
                for item in related
                if item.get(
                    "event_id"
                )
            ]

            if current_event_id:
                event_ids.append(
                    current_event_id
                )

            return create_incident(
                incident_type="web_attack",
                title="Suspicious Web Attack Activity",
                severity="HIGH",
                risk_score=86,
                confidence=0.91,
                source_ip=source_ip,
                username=username,
                related_events=list(
                    set(event_ids)
                ),
                explanation=(
                    f"{len(set(event_ids))} suspicious web requests "
                    "were detected from the same source within "
                    "a short time window."
                ),
                recommendation=(
                    "Inspect the affected application and source "
                    "requests. Review related web server logs and "
                    "consider blocking the source if confirmed malicious."
                ),
            )

    return None
