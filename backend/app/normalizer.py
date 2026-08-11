from datetime import datetime, timezone
from typing import Any


def first_value(data: dict[str, Any], *keys):
    """
    Return the first non-empty value found for the supplied keys.
    Supports common log field naming conventions.
    """
    for key in keys:
        value = data.get(key)

        if value is not None and value != "":
            return value

    return None


def parse_timestamp(data: dict[str, Any]):
    """
    Try common timestamp field names.
    Falls back to current UTC time.
    """
    value = first_value(
        data,
        "timestamp",
        "time",
        "@timestamp",
        "datetime",
        "date",
        "event_time"
    )

    if value is None:
        return datetime.now(timezone.utc)

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            pass

    return datetime.now(timezone.utc)


def normalize_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Convert arbitrary JSON security/log data into
    Sentinel's normalized SecurityEvent structure.

    The original payload is preserved under raw.
    """

    source_data = payload.get("source")

    if not isinstance(source_data, dict):
        source_data = {}

    actor_data = payload.get("actor")

    if not isinstance(actor_data, dict):
        actor_data = {}

    target_data = payload.get("target")

    if not isinstance(target_data, dict):
        target_data = {}

    event_data = payload.get("event")

    if not isinstance(event_data, dict):
        event_data = {}

    network_data = payload.get("network")

    if not isinstance(network_data, dict):
        network_data = {}

    # Source information
    source_id = first_value(
        source_data,
        "source_id",
        "id",
        "name"
    )

    if source_id is None:
        source_id = first_value(
            payload,
            "source_id",
            "hostname",
            "host",
            "device",
            "server",
            "source"
        )

    if source_id is None:
        source_id = "unknown-source"

    source_type = first_value(
        source_data,
        "source_type",
        "type"
    )

    if source_type is None:
        source_type = first_value(
            payload,
            "source_type",
            "log_type",
            "service",
            "source"
        )

    if source_type is None:
        source_type = "unknown"

    hostname = first_value(
        source_data,
        "hostname",
        "host",
        "computer"
    )

    if hostname is None:
        hostname = first_value(
            payload,
            "hostname",
            "host",
            "computer",
            "server"
        )

    source_ip = first_value(
        source_data,
        "ip",
        "source_ip",
        "src_ip"
    )

    if source_ip is None:
        source_ip = first_value(
            payload,
            "source_ip",
            "src_ip",
            "client_ip",
            "ip",
            "client"
        )

    # Actor information
    actor_ip = first_value(
        actor_data,
        "ip",
        "source_ip",
        "src_ip"
    )

    if actor_ip is None:
        actor_ip = source_ip

    username = first_value(
        actor_data,
        "user",
        "username",
        "account"
    )

    if username is None:
        username = first_value(
            payload,
            "user",
            "username",
            "account",
            "user_name"
        )

    country = first_value(
        actor_data,
        "country"
    )

    # Event information
    action = first_value(
        event_data,
        "action",
        "event_type",
        "type",
        "name"
    )

    if action is None:
        action = first_value(
            payload,
            "action",
            "event_type",
            "event",
            "type",
            "operation"
        )

    if action is None:
        action = "unknown"

    category = first_value(
        event_data,
        "category",
        "event_category"
    )

    if category is None:
        category = first_value(
            payload,
            "category",
            "event_category",
            "log_type"
        )

    if category is None:
        category = "general"

    status = first_value(
        event_data,
        "status",
        "result",
        "outcome"
    )

    if status is None:
        status = first_value(
            payload,
            "status",
            "result",
            "outcome"
        )

    if status is None:
        status = "unknown"

    severity = first_value(
        event_data,
        "severity",
        "level",
        "priority"
    )

    if severity is None:
        severity = first_value(
            payload,
            "severity",
            "level",
            "priority"
        )

    if severity is None:
        severity = "info"

    message = first_value(
        event_data,
        "message",
        "description",
        "msg"
    )

    if message is None:
        message = first_value(
            payload,
            "message",
            "description",
            "msg",
            "log"
        )

    if message is None:
        message = ""

    # Target information
    target_hostname = first_value(
        target_data,
        "hostname",
        "host",
        "server"
    )

    if target_hostname is None:
        target_hostname = first_value(
            payload,
            "target_hostname",
            "destination_host",
            "dst_host"
        )

    target_ip = first_value(
        target_data,
        "ip",
        "destination_ip",
        "dst_ip"
    )

    if target_ip is None:
        target_ip = first_value(
            payload,
            "destination_ip",
            "dst_ip",
            "target_ip"
        )

    resource = first_value(
        target_data,
        "resource",
        "path",
        "url"
    )

    if resource is None:
        resource = first_value(
            payload,
            "resource",
            "path",
            "url",
            "endpoint"
        )

    port = first_value(
        target_data,
        "port"
    )

    if port is None:
        port = first_value(
            payload,
            "port",
            "destination_port",
            "dst_port"
        )

    # Network information
    protocol = first_value(
        network_data,
        "protocol"
    )

    if protocol is None:
        protocol = first_value(
            payload,
            "protocol",
            "transport"
        )

    direction = first_value(
        network_data,
        "direction"
    )

    if direction is None:
        direction = first_value(
            payload,
            "direction"
        )

    network_port = first_value(
        network_data,
        "port"
    )

    if network_port is None:
        network_port = port

    # Event ID
    event_id = first_value(
        payload,
        "event_id",
        "id",
        "eventId",
        "uuid"
    )

    normalized = {
        "event_id": event_id,
        "timestamp": parse_timestamp(payload),

        "source": {
            "source_id": str(source_id),
            "source_type": str(source_type),
            "hostname": hostname,
            "ip": source_ip
        },

        "actor": {
            "ip": actor_ip,
            "user": username,
            "country": country
        },

        "target": {
            "hostname": target_hostname,
            "ip": target_ip,
            "resource": resource,
            "port": port
        },

        "event": {
            "category": str(category),
            "action": str(action),
            "status": str(status),
            "severity": str(severity),
            "message": str(message)
        },

        "network": {
            "protocol": protocol,
            "direction": direction,
            "port": network_port
        },

        "raw": {
            "original": payload
        }
    }

    return normalized
