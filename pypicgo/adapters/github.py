from __future__ import annotations

import base64
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

from .base import UploaderAdapter, register_adapter


@dataclass
class GitHubConfig:
    repo: str
    branch: str = "main"
    token: str = ""
    path: str = ""


@register_adapter("github")
class GitHubAdapter(UploaderAdapter):
    name = "github"

    def upload(self, files: List[str], config: Dict[str, Any]) -> List[str]:
        cfg = GitHubConfig(
            repo=config.get("repo", ""),
            branch=config.get("branch", "main"),
            token=config.get("token", ""),
            path=config.get("path", ""),
        )
        if not cfg.repo or not cfg.token:
            raise RuntimeError("github adapter requires repo and token")

        owner, repo = cfg.repo.split("/", 1)
        urls: List[str] = []
        for f in files:
            p = Path(f)
            rel = (cfg.path + "/" if cfg.path else "") + p.name
            sha = self._get_sha(owner, repo, rel, cfg)
            download_url = self._put_file(owner, repo, rel, cfg, p.read_bytes(), sha)
            urls.append(download_url)
        return urls

    def _request(self, method: str, url: str, token: str, data: bytes | None = None) -> Dict[str, Any]:
        req = urllib.request.Request(url=url, data=data, method=method)
        req.add_header("Authorization", f"token {token}")
        req.add_header("User-Agent", "pypicgo")
        req.add_header("Accept", "application/vnd.github+json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8"))

    def _get_sha(self, owner: str, repo: str, path: str, cfg: GitHubConfig) -> str | None:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={cfg.branch}"
        try:
            data = self._request("GET", url, cfg.token)
            return data.get("sha")
        except Exception:
            return None

    def _put_file(self, owner: str, repo: str, path: str, cfg: GitHubConfig, content: bytes, sha: str | None) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        payload = {
            "message": f"upload {Path(path).name} via pypicgo",
            "content": base64.b64encode(content).decode("ascii"),
            "branch": cfg.branch,
        }
        if sha:
            payload["sha"] = sha
        data = self._request("PUT", url, cfg.token, json.dumps(payload).encode("utf-8"))
        download_url = (
            (data.get("content") or {}).get("download_url")
            or f"https://raw.githubusercontent.com/{owner}/{repo}/{cfg.branch}/{path}"
        )
        return download_url


def _factory() -> UploaderAdapter:
    return GitHubAdapter()


# register_adapter("github", _factory)

