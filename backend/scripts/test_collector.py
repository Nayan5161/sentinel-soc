import socket
import time
from datetime import datetime, timezone

import requests


API_URL = "http://127.0.0.1:8000/api/ingest"
HOSTNAME = socket.gethostname()


def send_event(event_type, status, message, username=None):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "codespace-test-collector",
        "hostname": HOSTNAME,
        "src_ip": None,
        "username": username,
        "event_type": event_type,
        "status": status,
        "message": message,
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=10,
    )

    print(
        f"[{response.status_code}] "
        f"{event_type} -> "
        f"{response.json().get('status')}"
    )


if __name__ == "__main__":
    print("Sentinel test collector started")
    print(f"Hostname: {HOSTNAME}")
    print(f"API: {API_URL}")

    while True:
        send_event(
            event_type="collector_heartbeat",
            status="success",
            message="Test collector is running",
            username="codespace",
        )

        time.sleep(10)
