from datetime import datetime, timezone, timedelta

from bson import ObjectId
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from .config import APP_HOST, APP_PORT, CORS_ORIGINS
from .db import (
    events,
    systems,
    incidents,
    initialize_indexes,
    ping,
)
from .schemas import SecurityEvent
from .detection import analyze_event
from .analytics import calculate_dashboard
from .retention import (
    enforce_retention,
    get_collection_size_mb,
)
from .stream import subscribe, generate, publish


app = Flask(__name__)

CORS(
    app,
    origins=CORS_ORIGINS
)

initialize_indexes()


def serialize(document):
    if not document:
        return document

    document = dict(document)

    if "_id" in document:
        document["_id"] = str(document["_id"])

    return document


@app.get("/")
def index():
    return jsonify({
        "service": "Sentinel SOC Backend",
        "status": "running",
        "api": {
            "health": "/api/health",
            "dashboard": "/api/dashboard",
            "events": "/api/events",
            "stream": "/api/events/stream",
            "systems": "/api/systems",
            "incidents": "/api/incidents",
            "storage": "/api/storage"
        }
    })


@app.get("/api/health")
def health():
    try:
        ping()

        return jsonify({
            "status": "ok",
            "database": "connected",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        })

    except Exception as exc:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(exc)
        }), 503


@app.get("/api/dashboard")
def dashboard():
    try:
        now = datetime.now(timezone.utc)

        since = now - timedelta(hours=24)

        recent_events = list(
            events.find({
                "timestamp": {
                    "$gte": since
                }
            }).sort(
                "timestamp",
                -1
            )
        )

        system_list = list(
            systems.find({})
        )

        online_systems = sum(
            1
            for system in system_list
            if system.get("status") == "online"
        )

        dashboard_data = calculate_dashboard(
            recent_events,
            systems_count=len(system_list),
            online_systems=online_systems
        )

        dashboard_data["active_incidents"] = incidents.count_documents({
            "status": {
                "$in": [
                    "open",
                    "investigating"
                ]
            }
        })

        dashboard_data["live_activity"] = [
            serialize(event)
            for event in recent_events[:20]
        ]

        return jsonify(dashboard_data)

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 500


@app.post("/api/events")
def create_event():
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({
            "error": "JSON body required"
        }), 400

    try:
        validated = SecurityEvent.model_validate(
            payload
        )

        event = validated.model_dump(
            mode="python"
        )

        event = analyze_event(event)

        if not event.get("event_id"):
            event["event_id"] = str(ObjectId())

        event["received_at"] = datetime.now(
            timezone.utc
        )

        result = events.insert_one(event)

        event["_id"] = result.inserted_id

        # Enforce the 100 MB storage limit.
        enforce_retention()

        clean_event = serialize(event)

        # Immediately send the event to connected
        # real-time frontend clients.
        publish(clean_event)

        return jsonify({
            "status": "accepted",
            "event_id": event["event_id"],
            "event": clean_event
        }), 201

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 400


@app.get("/api/events")
def get_events():
    try:
        limit = min(
            int(request.args.get("limit", 50)),
            200
        )

        cursor = (
            events
            .find({})
            .sort(
                "timestamp",
                -1
            )
            .limit(limit)
        )

        return jsonify([
            serialize(event)
            for event in cursor
        ])

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 500


@app.get("/api/events/stream")
def event_stream():
    q = subscribe()

    return Response(
        generate(q),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@app.get("/api/storage")
def storage():
    try:
        size_mb = get_collection_size_mb()

        return jsonify({
            "collection": "events",
            "size_mb": round(
                size_mb,
                3
            ),
            "hard_limit_mb": 100,
            "cleanup_target_mb": 90,
            "usage_percent": round(
                (size_mb / 100) * 100,
                2
            )
        })

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 500


@app.get("/api/systems")
def get_systems():
    return jsonify([
        serialize(system)
        for system in systems.find({})
    ])


@app.get("/api/incidents")
def get_incidents():
    return jsonify([
        serialize(incident)
        for incident in incidents.find({})
    ])


if __name__ == "__main__":
    app.run(
        host=APP_HOST,
        port=APP_PORT,
        debug=False,
        threaded=True
    )
