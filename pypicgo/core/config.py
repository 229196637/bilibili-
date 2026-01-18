from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "default_host": "github",
    "format": "markdown",
    "copy_to_clipboard": True,
    "hosts": {
        "github": {
            "repo": "",
            "branch": "main",
            "token": "",
            "path": "",
        },
        "smms": {
            "token": "",
        },
        "bilibili": {
            "sessdata": "",
            "bili_jct": "",
        },
    },
    "history_enabled": True,
}


class ConfigManager:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(os.path.expanduser("~")) / ".pypicgo"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.base_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if self.config_path.exists():
            try:
                self._config = json.loads(self.config_path.read_text(encoding="utf-8"))
            except Exception:
                self._config = DEFAULT_CONFIG.copy()
        else:
            self._config = DEFAULT_CONFIG.copy()
            self.save()

    def save(self) -> None:
        self.config_path.write_text(json.dumps(self._config, ensure_ascii=False, indent=2), encoding="utf-8")

    @property
    def data(self) -> Dict[str, Any]:
        return self._config

    def get_host_config(self, host: str) -> Dict[str, Any]:
        hosts = self._config.get("hosts", {})
        return hosts.get(host, {})

    def set_host_config(self, host: str, cfg: Dict[str, Any]) -> None:
        self._config.setdefault("hosts", {})[host] = cfg
        self.save()

    def set_global_config(self, kv: Dict[str, Any]) -> None:
        self._config.update(kv)
        self.save()
