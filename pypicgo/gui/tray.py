from __future__ import annotations

import sys
import threading
from typing import Optional
from PIL import Image, ImageDraw

import pystray
from pystray import MenuItem as item

from ..core import PicGoCore
from ..core.watch import ClipboardWatcher


class TrayApp:
    def __init__(self) -> None:
        self.core = PicGoCore()
        self.watcher = ClipboardWatcher(self.core, self._on_status_change)
        self.icon: Optional[pystray.Icon] = None
        self._uploading = False

    def run(self) -> None:
        image = self._create_image()
        menu = pystray.Menu(
            item(
                "监听剪贴板",
                self._toggle_watch,
                checked=lambda item: self.watcher.running,
                radio=False
            ),
            pystray.Menu.SEPARATOR,
            item("退出", self._quit)
        )
        
        self.icon = pystray.Icon(
            "pypicgo",
            image,
            "PyPicGo - 剪贴板监听已就绪",
            menu
        )
        
        # Auto start watcher
        self.watcher.start()
        self.icon.run()

    def _create_image(self) -> Image.Image:
        # Create a simple icon with a 'P'
        width = 64
        height = 64
        color1 = (66, 133, 244)
        color2 = (255, 255, 255)
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.text((20, 15), "P", fill=color2, font_size=40)
        
        return image

    def _toggle_watch(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        if self.watcher.running:
            self.watcher.stop()
            icon.notify("已停止监听剪贴板图片", "PyPicGo")
        else:
            self.watcher.start()
            icon.notify("开始监听剪贴板图片...", "PyPicGo")

    def _quit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self.watcher.stop()
        icon.stop()

    def _on_status_change(self, status: str) -> None:
        if not self.icon:
            return
            
        if status == "uploading":
            self.icon.title = "PyPicGo - 正在上传..."
            # Note: notify might be annoying if triggered too often, uncomment if needed
            # self.icon.notify("发现图片，正在上传...", "PyPicGo")
            
        elif status == "uploaded":
            self.icon.title = "PyPicGo - 上传成功"
            self.icon.notify("上传成功！链接已复制", "PyPicGo")
            
        elif status.startswith("error"):
            self.icon.notify(f"上传失败: {status}", "PyPicGo")
            
        elif status == "running":
            self.icon.title = "PyPicGo - 监听中"
            
        elif status == "stopped":
            self.icon.title = "PyPicGo - 已停止"
