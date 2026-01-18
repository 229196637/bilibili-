import sys
import io
import os
import keyboard
import pyperclip
from PIL import ImageGrab, Image
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject, pyqtSignal, QBuffer, QIODevice
from PyQt6.QtGui import QIcon, QGuiApplication, QPixmap, QColor
from uploader import upload_bilibili

class Hotkey(QObject):
    trigger = pyqtSignal()
    def __init__(self):
        super().__init__()
        keyboard.add_hotkey('ctrl+alt+a', self.on_hotkey)
    def on_hotkey(self):
        self.trigger.emit()

class App(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.tray = QSystemTrayIcon(self.app)
        pm = QPixmap(16, 16)
        pm.fill(QColor("blue"))
        self.tray.setIcon(QIcon(pm))
        menu = QMenu()
        act = menu.addAction("Quit")
        act.triggered.connect(self.app.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()
        self.hk = Hotkey()
        self.hk.trigger.connect(self.process_clipboard)
        self.tray.showMessage("ScreenPhoto", "Press Ctrl+Alt+A to upload clipboard image.", QSystemTrayIcon.MessageIcon.Information, 2000)
    def process_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        mime = clipboard.mimeData()
        b = None
        if mime and mime.hasImage():
            qimg = clipboard.image()
            if not qimg.isNull():
                buf = QBuffer()
                buf.open(QIODevice.OpenModeFlag.ReadWrite)
                qimg.save(buf, "PNG")
                b = bytes(buf.data())
        else:
            c = ImageGrab.grabclipboard()
            if isinstance(c, Image.Image):
                buf = io.BytesIO()
                c.save(buf, format='PNG')
                b = buf.getvalue()
            elif isinstance(c, list):
                for p in c:
                    if os.path.isfile(p):
                        ext = os.path.splitext(p)[1].lower()
                        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
                            with open(p, 'rb') as f:
                                b = f.read()
                            break
        if not b:
            self.tray.showMessage("ScreenPhoto", "No image in clipboard.", QSystemTrayIcon.MessageIcon.Warning, 2000)
            return
        try:
            self.tray.showMessage("ScreenPhoto", "Uploading...", QSystemTrayIcon.MessageIcon.Information, 1000)
            url = upload_bilibili(b)
            pyperclip.copy(url)
            self.tray.showMessage("Upload Success", f"Link copied: {url}", QSystemTrayIcon.MessageIcon.Information, 3000)
        except Exception as e:
            self.tray.showMessage("Upload Failed", str(e), QSystemTrayIcon.MessageIcon.Critical, 5000)
    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    App().run()
