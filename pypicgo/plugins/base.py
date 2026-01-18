from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.pipeline import PicGoCore


class PluginBase(Protocol):
    def register(self, core: PicGoCore) -> None:
        ...

