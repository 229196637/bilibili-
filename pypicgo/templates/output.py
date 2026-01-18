from __future__ import annotations

from typing import List


def render_output(fmt: str, urls: List[str]) -> str:
    if fmt == "markdown":
        # Add a space after the closing parenthesis to avoid adjacent characters sticking to it
        return "\n".join([f"![]({u}) " for u in urls])
    if fmt == "html":
        return "\n".join([f"<img src=\"{u}\" />" for u in urls])
    if fmt == "url":
        return "\n".join(urls)
    return "\n".join(urls)

