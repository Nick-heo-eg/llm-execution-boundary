"""Approval Queue - Manages pending requests

The approval queue represents a deliberate pause in execution.
It marks the point where automated decision-making ends.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any


class ApprovalQueue:
    """Tracks requests requiring human approval"""

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self._ensure_store()

    def _ensure_store(self):
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps([], indent=2))

    def submit(self, request: Dict[str, Any]) -> str:
        """Submit request for approval. Returns approval ID.

        Requests reaching this queue are intentionally paused.
        Execution resumes only after explicit human approval.
        """
        approval_id = str(uuid.uuid4())

        record = {
            "approval_id": approval_id,
            "status": "pending",
            "request": request,
        }

        queue = self._load()
        queue.append(record)
        self._save(queue)

        return approval_id

    def _load(self) -> list:
        return json.loads(self.store_path.read_text())

    def _save(self, queue: list):
        self.store_path.write_text(json.dumps(queue, indent=2))
