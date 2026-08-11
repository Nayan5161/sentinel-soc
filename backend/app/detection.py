SUSPICIOUS_ACTIONS = {
    "brute_force",
    "bruteforce",
    "port_scan",
    "portscan",
    "privilege_escalation",
    "malware_detected",
    "malware",
    "unauthorized_access",
    "unauthorized_login",
}

AUTH_FAILURE_ACTIONS = {
    "login_attempt",
    "login_failed",
    "failed_login",
    "authentication",
    "authentication_failure",
    "auth_failure",
    "ssh_login_failed",
}

SUSPICIOUS_PATTERNS = (
    "../",
    "/etc/passwd",
    "/wp-admin",
    "/wp-login",
    "/phpmyadmin",
    "union select",
    "<script",
    "cmd.exe",
    "powershell",
    "wget ",
    "curl ",
)

SEVERITY_SCORES = {
    "info": 5,
    "low": 20,
    "medium": 50,
    "high": 75,
    "critical": 95,
}


def _severity_from_score(score):
    if score >= 90:
        return "CRITICAL"

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    if score >= 15:
        return "LOW"

    return "INFO"


def analyze_event(event):
    """
    Analyze one normalized Sentinel event.

    This is a deterministic rule-based engine.
    It does not invent events or modify the original raw payload.
    """

    details = event.get("event", {})

    action = str(
        details.get("action", "")
    ).lower().strip()

    status = str(
        details.get("status", "")
    ).lower().strip()

    message = str(
        details.get("message", "")
    ).lower()

    supplied_severity = str(
        details.get("severity", "info")
    ).lower().strip()

    actor = event.get("actor", {})

    username = str(
        actor.get("user") or ""
    ).lower()

    suspicious = False
    rule_id = None
    rule_name = None
    confidence = 0.0
    risk_score = SEVERITY_SCORES.get(
        supplied_severity,
        5
    )

    explanation = (
        "Routine system or application activity "
        "was observed."
    )

    recommendation = (
        "No immediate action required. "
        "Continue monitoring."
    )

    # ---------------------------------------------------------
    # Rule 1: Explicitly suspicious security actions
    # ---------------------------------------------------------

    if action in SUSPICIOUS_ACTIONS:
        suspicious = True
        rule_id = "SEC-001"
        rule_name = "Suspicious Security Action"
        confidence = 0.90

        risk_score = max(
            risk_score,
            85
        )

        explanation = (
            f"The event action '{action}' is associated "
            "with potentially malicious security activity."
        )

        recommendation = (
            "Investigate the source, affected account or "
            "resource, and related events."
        )

    # ---------------------------------------------------------
    # Rule 2: Suspicious request patterns
    # ---------------------------------------------------------

    elif any(
        pattern in message
        for pattern in SUSPICIOUS_PATTERNS
    ):
        suspicious = True
        rule_id = "WEB-001"
        rule_name = "Suspicious Request Pattern"
        confidence = 0.93

        risk_score = max(
            risk_score,
            80
        )

        explanation = (
            "The event contains a request pattern commonly "
            "associated with web exploitation or command execution."
        )

        recommendation = (
            "Inspect the source request, affected application, "
            "and nearby web/server events."
        )

    # ---------------------------------------------------------
    # Rule 3: Failed authentication
    # ---------------------------------------------------------

    elif (
        action in AUTH_FAILURE_ACTIONS
        and status in {
            "failed",
            "failure",
            "denied",
            "rejected"
        }
    ):
        suspicious = True
        rule_id = "AUTH-001"
        rule_name = "Failed Authentication"
        confidence = 0.75

        risk_score = max(
            risk_score,
            65
        )

        explanation = (
            "A failed authentication attempt was detected."
        )

        recommendation = (
            "Review the source IP, target account, and "
            "nearby authentication failures."
        )

        if username in {
            "root",
            "admin",
            "administrator",
            "sudo"
        }:
            risk_score = max(
                risk_score,
                75
            )

            confidence = 0.85

            explanation = (
                "A failed authentication attempt targeted "
                "a privileged account."
            )

            recommendation = (
                "Immediately review the source IP and "
                "verify whether the privileged account "
                "activity was authorized."
            )

    # ---------------------------------------------------------
    # Rule 4: Critical events
    # ---------------------------------------------------------

    elif supplied_severity == "critical":
        suspicious = True
        rule_id = "SEC-CRITICAL"
        rule_name = "Critical Security Event"
        confidence = 0.98

        risk_score = 95

        explanation = (
            "The source event was classified as critical "
            "by the originating system."
        )

        recommendation = (
            "Investigate immediately and determine whether "
            "containment or remediation is required."
        )

    # ---------------------------------------------------------
    # Rule 5: High-severity events
    # ---------------------------------------------------------

    elif supplied_severity == "high":
        risk_score = max(
            risk_score,
            75
        )

        explanation = (
            "The originating system classified this event "
            "as high severity."
        )

        recommendation = (
            "Review the event and related activity "
            "for signs of escalation."
        )

    # ---------------------------------------------------------
    # System telemetry is not automatically a threat
    # ---------------------------------------------------------

    if action == "system_telemetry":
        suspicious = False
        rule_id = None
        rule_name = None
        confidence = 0.0

        risk_score = 5

        explanation = (
            "Live system health telemetry was collected "
            "from the monitored endpoint."
        )

        recommendation = (
            "Continue monitoring CPU, memory, disk, "
            "and system availability."
        )

    calculated_severity = _severity_from_score(
        risk_score
    )

    event["detection"] = {
        "suspicious": suspicious,
        "rule_id": rule_id,
        "rule_name": rule_name,
        "confidence": round(
            confidence,
            2
        ),
    }

    event["analysis"] = {
        "risk_score": int(
            max(
                0,
                min(
                    risk_score,
                    100
                )
            )
        ),
        "severity": calculated_severity,
        "confidence": round(
            confidence,
            2
        ),
        "suspicious": suspicious,
        "rule_id": rule_id,
        "rule_name": rule_name,
        "explanation": explanation,
        "recommendation": recommendation,
    }

    return event
