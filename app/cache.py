import time


class TTLCache:
    """In-memory cache for rarely changing lookups (authors, genres)."""

    def __init__(self, ttl: float = 30.0):
        self.ttl = ttl
        self._data: dict[str, tuple[float, object]] = {}

    def get(self, key: str):
        item = self._data.get(key)
        if item and time.monotonic() - item[0] < self.ttl:
            return item[1]
        return None

    def set(self, key: str, value) -> None:
        self._data[key] = (time.monotonic(), value)

    def invalidate(self) -> None:
        self._data.clear()


cache = TTLCache()
