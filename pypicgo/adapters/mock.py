from typing import List
from pathlib import Path
import time
import random
from .base import UploaderAdapter, register_adapter

@register_adapter("mock")
class MockUploader(UploaderAdapter):
    def upload(self, files: List[str], config: dict) -> List[str]:
        urls = []
        base_url = config.get("base_url", "https://mock.example.com")
        for file in files:
            # Simulate network delay
            time.sleep(0.5)
            # Generate fake URL
            filename = Path(file).name
            random_hash = "".join(random.choices("abcdef0123456789", k=8))
            urls.append(f"{base_url}/{random_hash}/{filename}")
        return urls
