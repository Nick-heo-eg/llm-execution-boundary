"""Audit Logger - Immutable event log"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any


class AuditLogger:
    """Append-only audit log for execution decisions"""

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self._ensure_store()

    def _ensure_store(self):
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps([], indent=2))

    def log_event(
        self,
        request_id: str,
        decision: str,
        rule_id: str,
        reason: str,
        metadata: Dict[str, Any],
    ) -> str:
        """Log execution decision. Returns event ID."""
        event_id = str(uuid.uuid4())

        event = {
            "event_id": event_id,
            "timestamp": time.time(),
            "request_id": request_id,
            "decision": decision,
            "rule_id": rule_id,
            "reason": reason,
            "metadata": metadata,
        }

        events = self._load()
        events.append(event)
        self._save(events)

        return event_id

    def _load(self) -> list:
        return json.loads(self.store_path.read_text())

    def _save(self, events: list):
        self.store_path.write_text(json.dumps(events, indent=2))
