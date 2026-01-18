from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.pipeline import PicGoCore


def load_plugins(core: PicGoCore) -> List[str]:
    loaded: List[str] = []
    try:
        from importlib.metadata import entry_points

        eps = entry_points()
        group = eps.select if hasattr(eps, "select") else None
        entries = group(group="pypicgo.plugins") if group else eps.get("pypicgo.plugins", [])
        for ep in entries:
            try:
                plugin_cls = ep.load()
                plugin = plugin_cls()
                plugin.register(core)
                loaded.append(ep.name)
            except Exception:
                continue
    except Exception:
        pass
    return loaded

