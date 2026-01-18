import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from pypicgo.gui.tray import TrayApp

if __name__ == "__main__":
    app = TrayApp()
    app.run()
