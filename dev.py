import os
import sys
import time
import signal
import socket
import subprocess
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")

processes = []


def log(prefix, line):
    print(f"[{prefix}] {line}", flush=True)


def stream_output(prefix, process):
    for line in iter(process.stdout.readline, ""):
        if line:
            log(prefix, line.rstrip())


def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def start_process(prefix, command, cwd, env=None):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    processes.append((prefix, process))

    thread = threading.Thread(
        target=stream_output,
        args=(prefix, process),
        daemon=True,
    )
    thread.start()

    return process


def wait_for_port(port, name, timeout=30):
    start = time.time()

    while time.time() - start < timeout:
        if not port_free(port):
            log("SYSTEM", f"{name} is ready on port {port}")
            return True

        time.sleep(0.5)

    log("SYSTEM", f"ERROR: {name} did not start on port {port}")
    return False


def shutdown(signum=None, frame=None):
    print("\n[SYSTEM] Stopping Sentinel...", flush=True)

    for prefix, process in reversed(processes):
        if process.poll() is None:
            log("SYSTEM", f"Stopping {prefix}")
            process.terminate()

    time.sleep(2)

    for prefix, process in reversed(processes):
        if process.poll() is None:
            process.kill()

    print("[SYSTEM] Sentinel stopped.", flush=True)
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


print()
print("=" * 60)
print("              SENTINEL SOC DEV STACK")
print("=" * 60)
print()
print("[SYSTEM] Starting Sentinel...")
print()


# ---------------------------------------------------------
# Check ports
# ---------------------------------------------------------

if not port_free(8000):
    print("[SYSTEM] ERROR: Port 8000 is already in use.")
    print("[SYSTEM] Stop the existing backend before starting dev.py.")
    sys.exit(1)

if not port_free(5173):
    print("[SYSTEM] ERROR: Port 5173 is already in use.")
    print("[SYSTEM] Stop the existing frontend before starting dev.py.")
    sys.exit(1)


# ---------------------------------------------------------
# Backend
# ---------------------------------------------------------

backend_env = os.environ.copy()

backend_python = os.path.join(
    BACKEND,
    ".venv",
    "bin",
    "python",
)

if not os.path.exists(backend_python):
    backend_python = sys.executable

log("SYSTEM", "Starting backend on :8000")

backend = start_process(
    "BACKEND",
    [
        backend_python,
        "run.py",
    ],
    BACKEND,
    backend_env,
)


if not wait_for_port(8000, "Backend"):
    shutdown()


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

log("SYSTEM", "Starting frontend on :5173")

frontend_env = os.environ.copy()

frontend = start_process(
    "FRONTEND",
    [
        "npm",
        "run",
        "dev",
        "--",
        "--host",
        "0.0.0.0",
        "--port",
        "5173",
    ],
    FRONTEND,
    frontend_env,
)


if not wait_for_port(5173, "Frontend"):
    shutdown()


# ---------------------------------------------------------
# Test Collector
# ---------------------------------------------------------

log("SYSTEM", "Starting test collector")

collector = start_process(
    "COLLECTOR",
    [
        backend_python,
        "scripts/test_collector.py",
    ],
    BACKEND,
    backend_env,
)


# ---------------------------------------------------------
# Ready
# ---------------------------------------------------------

print()
print("=" * 60)
print("              SENTINEL SOC READY")
print("=" * 60)
print()
print("Frontend : http://localhost:5173")
print("Backend  : http://localhost:8000")
print("Health   : http://localhost:8000/api/health")
print("SSE      : http://localhost:8000/api/events/stream")
print()
print("Running:")
print("  [BACKEND]   Flask API")
print("  [FRONTEND]  Vite React")
print("  [COLLECTOR] Test event collector")
print()
print("Press Ctrl+C to stop everything.")
print("=" * 60)
print()

# Keep launcher alive.
while True:
    for prefix, process in processes:
        if process.poll() is not None:
            log(
                "SYSTEM",
                f"{prefix} exited with code {process.returncode}",
            )

    time.sleep(2)
