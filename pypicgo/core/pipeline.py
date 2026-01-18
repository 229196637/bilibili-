from __future__ import annotations

from pathlib import Path
from typing import List

from .events import EventBus, Phase, Context
from .config import ConfigManager
from .history import HistoryStore
from ..adapters import get_adapter
from ..templates.output import render_output
from ..plugins.loader import load_plugins
from .clipboard import copy_text


class PicGoCore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.events = EventBus()
        self.config = ConfigManager(base_dir)
        history_path = (self.config.base_dir / "history.json")
        self.history = HistoryStore(history_path)
        load_plugins(self)

    def run(self, files: List[str], host: str | None = None, fmt: str | None = None) -> str:
        host = host or self.config.data.get("default_host", "github")
        fmt = fmt or self.config.data.get("format", "markdown")
        ctx = Context(files=files, host=host, config=self.config.get_host_config(host))

        ctx = self.events.run(Phase.INPUT, ctx)
        ctx = self.events.run(Phase.BEFORE_UPLOAD, ctx)

        adapter = get_adapter(host)
        if adapter is None:
            raise RuntimeError(f"no adapter registered for host: {host}")
        urls = adapter.upload(ctx.files, ctx.config)
        ctx.urls = urls

        ctx = self.events.run(Phase.AFTER_UPLOAD, ctx)
        output_text = render_output(fmt, urls)
        ctx.output_text = output_text

        if self.config.data.get("history_enabled", True) and urls:
            self.history.add(files=ctx.files, host=host, urls=urls)
        if self.config.data.get("copy_to_clipboard", True) and output_text:
            copy_text(output_text)
        return output_text
