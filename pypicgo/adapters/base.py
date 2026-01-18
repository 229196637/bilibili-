from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable

_registry: Dict[str, "UploaderAdapter"] = {}


class UploaderAdapter(ABC):
    name: str

    @abstractmethod
    def upload(self, files: List[str], config: Dict[str, Any]) -> List[str]:
        ...


def register_adapter(name: str):
    def decorator(cls):
        _registry[name] = cls()
        return cls
    return decorator


def get_adapter(name: str) -> UploaderAdapter | None:
    return _registry.get(name)

