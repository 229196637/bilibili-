from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Any


class Phase(str, Enum):
    INPUT = "input"
    BEFORE_UPLOAD = "before_upload"
    UPLOAD = "upload"
    AFTER_UPLOAD = "after_upload"


Hook = Callable[["Context"], "Context"]


@dataclass
class Context:
    files: List[str]
    host: str
    config: Dict[str, Any]
    urls: List[str] | None = None
    output_text: str | None = None


class EventBus:
    def __init__(self) -> None:
        self._hooks: Dict[Phase, List[Hook]] = {
            Phase.INPUT: [],
            Phase.BEFORE_UPLOAD: [],
            Phase.UPLOAD: [],
            Phase.AFTER_UPLOAD: [],
        }

    def add_hook(self, phase: Phase, func: Hook) -> None:
        self._hooks.setdefault(phase, []).append(func)

    def remove_hook(self, phase: Phase, func: Hook) -> None:
        hooks = self._hooks.get(phase, [])
        if func in hooks:
            hooks.remove(func)

    def run(self, phase: Phase, ctx: Context) -> Context:
        for hook in self._hooks.get(phase, []):
            ctx = hook(ctx)
        return ctx

