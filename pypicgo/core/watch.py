from __future__ import annotations

import time
import threading
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageGrab
from typing import Callable, Optional

from .pipeline import PicGoCore


class ClipboardWatcher:
    def __init__(self, core: PicGoCore, on_status_change: Optional[Callable[[str], None]] = None) -> None:
        self.core = core
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.on_status_change = on_status_change
        self._last_image_data: Optional[bytes] = None

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        if self.on_status_change:
            self.on_status_change("running")

    def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)
        if self.on_status_change:
            self.on_status_change("stopped")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._check_clipboard()
            except Exception as e:
                print(f"Clipboard check error: {e}")
            time.sleep(1)  # check every 1 second

    def _check_clipboard(self) -> None:
        # Grab clipboard content
        # Note: grabclipboard() returns Image object for images, list for files, None for others
        try:
            content = ImageGrab.grabclipboard()
        except Exception:
            return

        if isinstance(content, Image.Image):
            # Check for duplicate image to prevent infinite loops or redundant uploads
            # We compare raw bytes of the image
            from io import BytesIO
            with BytesIO() as b:
                content.save(b, "PNG")
                current_data = b.getvalue()
            
            if self._last_image_data == current_data:
                return
            
            self._last_image_data = current_data
            self._handle_image(content)
        else:
            # If clipboard content is not an image (e.g. text), clear last image data
            self._last_image_data = None

    def _handle_image(self, img: Image.Image) -> None:
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            img.save(tmp_path, "PNG")
            
            # Notify uploading (if callback available)
            if self.on_status_change:
                self.on_status_change("uploading")

            # Upload using core
            # core.run will handle clipboard copying of the result URL
            self.core.run([tmp_path])
            
            if self.on_status_change:
                self.on_status_change("uploaded")
                
        except Exception as e:
            print(f"Upload failed: {e}")
            if self.on_status_change:
                self.on_status_change(f"error: {e}")
        finally:
            # Cleanup temp file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
