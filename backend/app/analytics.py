from datetime import datetime, timezone, timedelta


def calculate_dashboard(events, systems_count=0, online_systems=0):
    now = datetime.now(timezone.utc)

    total = len(events)

    suspicious = sum(
        1
        for e in events
        if e.get("detection", {}).get("suspicious") is True
    )

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    }

    for event in events:
        severity = (
            event
            .get("event", {})
            .get("severity", "info")
            .lower()
        )

        if severity in severity_counts:
            severity_counts[severity] += 1

    critical = severity_counts["critical"]
    high = severity_counts["high"]
    medium = severity_counts["medium"]

    if critical > 0:
        threat_level = "CRITICAL"
    elif high >= 3 or suspicious >= 5:
        threat_level = "HIGH"
    elif high > 0 or suspicious > 0:
        threat_level = "ELEVATED"
    else:
        threat_level = "NORMAL"

    # Transparent deterministic score.
    security_score = 100

    security_score -= critical * 15
    security_score -= high * 7
    security_score -= medium * 3
    security_score -= suspicious * 2

    security_score = max(
        0,
        min(100, security_score)
    )

    return {
        "generated_at": now.isoformat(),
        "timezone": "Asia/Kolkata",

        "security_score": security_score,

        "threat_level": threat_level,

        "events": {
            "total": total,
            "suspicious": suspicious
        },

        "severity": severity_counts,

        "systems": {
            "total": systems_count,
            "online": online_systems,
            "offline": max(
                0,
                systems_count - online_systems
            )
        },

        "threat_trend": []
    }
