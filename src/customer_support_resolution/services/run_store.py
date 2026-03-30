"""File-backed persistence for workflow runs."""

from __future__ import annotations

import json
from pathlib import Path

from customer_support_resolution.domain.models import RunSummary


class RunStore:
    """Persists run summaries and graph state snapshots to disk."""

    def __init__(self, base_dir: Path | None = None) -> None:
        root = base_dir or Path.cwd() / ".customer_support_resolution"
        self.base_dir = root
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, run: RunSummary, graph_state: dict[str, object]) -> None:
        path = self.base_dir / f"{run.run_id}.json"
        payload = {
            "run": run.model_dump(mode="json"),
            "graph_state": graph_state,
        }
        path.write_text(json.dumps(payload, indent=2))

    def load_run(self, run_id: str) -> RunSummary | None:
        path = self.base_dir / f"{run_id}.json"
        if not path.exists():
            return None
        payload = json.loads(path.read_text())
        return RunSummary.model_validate(payload["run"])
