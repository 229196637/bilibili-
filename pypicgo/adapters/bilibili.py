from __future__ import annotations

import json
import mimetypes
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

from .base import UploaderAdapter, register_adapter


@dataclass
class BilibiliConfig:
    sessdata: str = ""
    bili_jct: str = ""


@register_adapter("bilibili")
class BilibiliAdapter(UploaderAdapter):
    name = "bilibili"

    def upload(self, files: List[str], config: Dict[str, Any]) -> List[str]:
        cfg = BilibiliConfig(
            sessdata=config.get("sessdata", ""),
            bili_jct=config.get("bili_jct", ""),
        )
        if not cfg.sessdata or not cfg.bili_jct:
            raise RuntimeError("bilibili adapter requires sessdata and bili_jct")

        urls: List[str] = []
        for f in files:
            urls.append(self._upload_one(Path(f), cfg))
        return urls

    def _upload_one(self, path: Path, cfg: BilibiliConfig) -> str:
        # Use Bilibili dynamic API (Newer endpoint)
        url = "https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs"
        
        # Build multipart body manually to avoid external dependencies like requests
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = self._multipart_body(boundary, path, cfg.bili_jct)
        
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        # Cookie must contain SESSDATA and bili_jct
        # Ensure SESSDATA is passed as is (assuming user provided correct encoded/decoded value)
        req.add_header("Cookie", f"SESSDATA={cfg.sessdata}; bili_jct={cfg.bili_jct}")
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        req.add_header("Referer", "https://t.bilibili.com/")
        req.add_header("Origin", "https://t.bilibili.com")
        req.add_header("Host", "api.bilibili.com")

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            if e.code == 403:
                raise RuntimeError(f"Bilibili upload failed (403 Forbidden). Response: {error_body}") from e
            raise RuntimeError(f"Bilibili upload failed with HTTP {e.code}. Response: {error_body}") from e

        if data.get("code") == 0:
            url = (data.get("data") or {}).get("image_url")
            if url and url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
            return url
        
        raise RuntimeError(f"bilibili upload failed: {data}")

    def _multipart_body(self, boundary: str, path: Path, csrf: str) -> bytes:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts: List[bytes] = []
        
        # Add file_up
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(f'Content-Disposition: form-data; name="file_up"; filename="{path.name}"\r\n'.encode("utf-8"))
        parts.append(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
        parts.append(path.read_bytes())
        parts.append("\r\n".encode("utf-8"))
        
        # Add biz (must be 'draw')
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append('Content-Disposition: form-data; name="biz"\r\n\r\n'.encode("utf-8"))
        parts.append("draw\r\n".encode("utf-8"))
        
        # Add category (must be 'daily')
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append('Content-Disposition: form-data; name="category"\r\n\r\n'.encode("utf-8"))
        parts.append("daily\r\n".encode("utf-8"))

        # Add csrf (bili_jct) - required for newer API
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append('Content-Disposition: form-data; name="csrf"\r\n\r\n'.encode("utf-8"))
        parts.append(f"{csrf}\r\n".encode("utf-8"))
        
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        return b"".join(parts)
