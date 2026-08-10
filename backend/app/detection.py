SUSPICIOUS_ACTIONS = {
    "brute_force",
    "port_scan",
    "privilege_escalation",
    "malware_detected",
    "unauthorized_access",
}

SUSPICIOUS_PATTERNS = (
    "../",
    "/etc/passwd",
    "/wp-admin",
    "/wp-login",
    "/phpmyadmin",
    "union select",
    "<script",
)


def analyze_event(event):
    details = event.get("event", {})
    action = str(details.get("action", "")).lower()
    status = str(details.get("status", "")).lower()
    message = str(details.get("message", "")).lower()
    severity = str(details.get("severity", "info")).lower()

    suspicious = False
    rule_id = None
    rule_name = None
    confidence = 0.0

    if action in SUSPICIOUS_ACTIONS:
        suspicious = True
        rule_id = "SEC-001"
        rule_name = "Suspicious Security Action"
        confidence = 0.90

    elif any(pattern in message for pattern in SUSPICIOUS_PATTERNS):
        suspicious = True
        rule_id = "WEB-001"
        rule_name = "Suspicious Request Pattern"
        confidence = 0.93

    elif (
        action in {"login_attempt", "authentication"}
        and status == "failed"
    ):
        suspicious = True
        rule_id = "AUTH-001"
        rule_name = "Failed Authentication"
        confidence = 0.75

    elif severity == "critical":
        suspicious = True
        rule_id = "SEC-CRITICAL"
        rule_name = "Critical Security Event"
        confidence = 0.98

    event["detection"] = {
        "suspicious": suspicious,
        "rule_id": rule_id,
        "rule_name": rule_name,
        "confidence": confidence,
    }

    return event
