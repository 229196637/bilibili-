from __future__ import annotations

import subprocess


def copy_text(text: str) -> None:
    try:
        import pyperclip  # type: ignore

        pyperclip.copy(text)
        return
    except Exception:
        pass
    
    # Windows native clip command
    try:
        import platform
        if platform.system() == "Windows":
            subprocess.run("clip", input=text.encode("gbk", errors="ignore"), check=True)
            return
    except Exception:
        pass

    try:
        p = subprocess.Popen(["powershell", "-Command", "Set-Clipboard"], stdin=subprocess.PIPE)
        assert p.stdin is not None
        p.stdin.write(text.encode("utf-8"))
        p.stdin.close()
        p.wait(timeout=2)
    except Exception:
        pass

