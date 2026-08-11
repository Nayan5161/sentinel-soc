import os
import socket
import time
import platform
from datetime import datetime, timezone

import psutil
import requests


API_URL = os.getenv(
    "SENTINEL_API_URL",
    "http://127.0.0.1:8000"
)

HOSTNAME = socket.gethostname()


def get_local_ip():
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:
        return "127.0.0.1"


def collect_telemetry():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "source": {
            "source_id": HOSTNAME,
            "source_type": "system_telemetry",
            "hostname": HOSTNAME,
            "ip": get_local_ip()
        },

        "actor": {
            "user": os.getenv(
                "USER",
                "codespace"
            )
        },

        "target": {
            "hostname": HOSTNAME
        },

        "event": {
            "category": "system",
            "action": "system_telemetry",
            "status": "success",
            "severity": "info",
            "message": "Live system telemetry"
        },

        "network": {
            "protocol": "local",
            "direction": "internal"
        },

        "telemetry": {
            "cpu_percent": psutil.cpu_percent(
                interval=0.5
            ),
            "memory_percent": memory.percent,
            "memory_available_mb": round(
                memory.available / (1024 * 1024),
                2
            ),
            "disk_percent": disk.percent,
            "disk_free_gb": round(
                disk.free / (1024 * 1024 * 1024),
                2
            ),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "uptime_seconds": int(
                time.time() - psutil.boot_time()
            )
        }
    }


def send_telemetry():
    payload = collect_telemetry()

    response = requests.post(
        f"{API_URL}/api/events",
        json=payload,
        timeout=10
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "HTTP",
        response.status_code
    )

    if response.status_code != 201:
        print(response.text)


if __name__ == "__main__":
    print(
        f"Sentinel telemetry agent → {API_URL}"
    )

    while True:
        try:
            send_telemetry()

        except Exception as exc:
            print(
                "Telemetry error:",
                exc
            )

        time.sleep(10)
