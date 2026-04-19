import json
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional


LEVEL_INFO = 0
LEVEL_WARN = 1
LEVEL_ERROR = 2
LEVEL_DEBUG = 3


class Olympus:
    def __init__(
        self,
        api_key: str,
        service: str,
        endpoint: str = "http://localhost:4000",
        flush_interval: float = 10.0,
        batch_size: int = 100,
    ):
        if not api_key:
            raise ValueError("Olympus: api_key is required")
        if not service:
            raise ValueError("Olympus: service name is required")

        self._api_key = api_key
        self._service = service
        self._endpoint = endpoint
        self._flush_interval = flush_interval
        self._batch_size = batch_size
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._running = True

        self._timer = threading.Thread(target=self._auto_flush, daemon=True)
        self._timer.start()

    def info(self, message: str) -> None:
        self._push(LEVEL_INFO, message)

    def warn(self, message: str) -> None:
        self._push(LEVEL_WARN, message)

    def error(self, message: str) -> None:
        self._push(LEVEL_ERROR, message)

    def debug(self, message: str) -> None:
        self._push(LEVEL_DEBUG, message)

    def _push(self, level: int, message: str) -> None:
        entry = {
            "level": level,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self._buffer.append(entry)
            should_flush = len(self._buffer) >= self._batch_size

        if should_flush:
            self.flush()

    def flush(self) -> Optional[str]:
        with self._lock:
            if not self._buffer:
                return None
            logs = self._buffer[: self._batch_size]
            self._buffer = self._buffer[self._batch_size :]

        payload = json.dumps({"service": self._service, "logs": logs}).encode("utf-8")

        req = urllib.request.Request(
            f"{self._endpoint}/api/v1/ingest",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 201:
                    return None
                # Put logs back on non-201
                with self._lock:
                    self._buffer = logs + self._buffer
                return f"[Olympus] Server returned {resp.status}"
        except urllib.error.HTTPError as e:
            with self._lock:
                self._buffer = logs + self._buffer
            return f"[Olympus] HTTP error: {e.code}"
        except Exception as e:
            with self._lock:
                self._buffer = logs + self._buffer
            return f"[Olympus] Network error: {e}"

    def _auto_flush(self) -> None:
        while self._running:
            time.sleep(self._flush_interval)
            err = self.flush()
            if err:
                print(err)

    def close(self) -> None:
        self._running = False
        self.flush()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
