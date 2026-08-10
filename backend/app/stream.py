import json
import queue
import threading

subscribers = set()
lock = threading.Lock()


def subscribe():
    """Create and register a queue for one SSE client."""
    client_queue = queue.Queue()

    with lock:
        subscribers.add(client_queue)

    return client_queue


def unsubscribe(client_queue):
    """Remove an SSE client."""
    with lock:
        subscribers.discard(client_queue)


def publish(data):
    """Send an event to every connected SSE client."""
    message = json.dumps(data, default=str)

    with lock:
        clients = list(subscribers)

    for client_queue in clients:
        client_queue.put(message)


def generate(client_queue):
    """Generate Server-Sent Events for one client."""
    try:
        while True:
            message = client_queue.get()

            yield (
                "event: security_event\n"
                f"data: {message}\n\n"
            )

    finally:
        unsubscribe(client_queue)
