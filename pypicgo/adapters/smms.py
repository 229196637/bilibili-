from __future__ import annotations

import json
import mimetypes
import os
import uuid
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

from .base import UploaderAdapter, register_adapter


@dataclass
class SMMSConfig:
    token: str = ""


@register_adapter("smms")
class SMMSAdapter(UploaderAdapter):
    name = "smms"

    def upload(self, files: List[str], config: Dict[str, Any]) -> List[str]:
        cfg = SMMSConfig(token=config.get("token", ""))
        if not cfg.token:
            raise RuntimeError("sm.ms adapter requires token")
        urls: List[str] = []
        for f in files:
            urls.append(self._upload_one(Path(f), cfg))
        return urls

    def _upload_one(self, path: Path, cfg: SMMSConfig) -> str:
        boundary = uuid.uuid4().hex
        body = self._multipart_body(boundary, path)
        req = urllib.request.Request("https://sm.ms/api/v2/upload", data=body, method="POST")
        req.add_header("Authorization", cfg.token)
        req.add_header("User-Agent", "pypicgo")
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("success"):
            return (data.get("data") or {}).get("url")
        # fallback for duplicate image\n
        if data.get("code") == "image_repeated":
            return (data.get("images") or "")
        raise RuntimeError(f"sm.ms upload failed: {data}")

    def _multipart_body(self, boundary: str, path: Path) -> bytes:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts: List[bytes] = []
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            f'Content-Disposition: form-data; name="smfile"; filename="{path.name}"\r\n'.encode("utf-8")
        )
        parts.append(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
        parts.append(path.read_bytes())
        parts.append("\r\n".encode("utf-8"))
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        return b"".join(parts)


def _factory() -> UploaderAdapter:
    return SMMSAdapter()


# register_adapter("smms", _factory)

