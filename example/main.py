import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from olympus import Olympus

api_key = os.getenv("OLYMPUS_API_KEY", "ol_YOUR_KEY_HERE")

with Olympus(
    api_key=api_key,
    service="my-python-app",
    endpoint="http://localhost:4000",
    flush_interval=5.0,
) as client:
    client.info("Application started")
    client.info("Connected to database")
    client.warn("Cache miss for key=user:profile:123")
    client.error("Failed to process payment — timeout after 30s")
    client.debug("Query executed in 42ms")

    print("Logs buffered. Flushing...")
    client.flush()
    print("Done!")
