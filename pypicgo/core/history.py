from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class HistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _write(self, data: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, files: List[str], host: str, urls: List[str]) -> None:
        data = self._read()
        data.append(
            {
                "time": datetime.utcnow().isoformat() + "Z",
                "host": host,
                "files": files,
                "urls": urls,
            }
        )
        self._write(data)

    def list(self) -> List[Dict[str, Any]]:
        return self._read()

    def clear(self) -> None:
        self._write([])

