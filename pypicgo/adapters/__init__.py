from .base import UploaderAdapter, register_adapter, get_adapter
from .github import GitHubAdapter  # register side-effect
from .smms import SMMSAdapter  # register side-effect
from .bilibili import BilibiliAdapter  # register side-effect
from .mock import MockUploader  # register side-effect

__all__ = ["UploaderAdapter", "register_adapter", "get_adapter"]
