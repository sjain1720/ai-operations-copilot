import base64
import json
from datetime import datetime
from typing import Tuple


def encode_cursor(timestamp: datetime, identifier: int) -> str:
    payload = {"timestamp": timestamp.isoformat(), "id": identifier}
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(encoded).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> Tuple[datetime, int]:
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode((cursor + padding).encode("ascii"))
        )
        timestamp = datetime.fromisoformat(payload["timestamp"])
        identifier = int(payload["id"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid pagination cursor") from exc

    if timestamp.tzinfo is None or identifier <= 0:
        raise ValueError("Invalid pagination cursor")
    return timestamp, identifier
