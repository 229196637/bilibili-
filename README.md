# PyPicGo

A Python implementation of [PicGo](https://github.com/Molunerfinn/PicGo), a lightweight tool for uploading images to various cloud storage services.

## Features

- **CLI Interface**: Easy-to-use command line interface.
- **HTTP API**: Built-in HTTP server for integration with other tools (like Typora, Obsidian).
- **Multiple Hosts**: 
  - **GitHub**: Upload to GitHub repository.
  - **SM.MS**: Upload to SM.MS.
  - **Bilibili**: Upload to Bilibili dynamic feed (requires SESSDATA).
  - **Mock**: For testing purposes.
- **Clipboard Support**: Automatically copy uploaded links to clipboard.
- **Multiple Formats**: Markdown, HTML, URL, UBB, Custom.

## Installation

### Prerequisites
- Python 3.8+
- Git

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/pypicgo.git
   cd pypicgo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You can configure PyPicGo using the CLI. The configuration file is stored at `~/.pypicgo/config.json`.

**Note for Windows Users**: A `pypicgo.bat` script is provided for convenience. You can use `.\pypicgo.bat` instead of `python -m pypicgo.cli.main`.

### 1. Configure GitHub
```bash
# Set Token (Required)
.\pypicgo.bat config set --host github --kv token=YOUR_GITHUB_TOKEN

# Set Repository (Required, format: username/repo)
.\pypicgo.bat config set --host github --kv repo=username/repo

# Set Branch (Optional, default: main)
.\pypicgo.bat config set --host github --kv branch=main

# Set Path (Optional, folder prefix)
.\pypicgo.bat config set --host github --kv path=images
```

### 2. Configure Bilibili
To use Bilibili as an image host, you need to get your cookies (`SESSDATA` and `bili_jct`) from your browser.
1. Log in to [bilibili.com](https://www.bilibili.com).
2. Open Developer Tools (F12) -> Application -> Cookies.
3. Find `SESSDATA` and `bili_jct`.

```bash
.\pypicgo.bat config set --host bilibili --kv sessdata=YOUR_SESSDATA bili_jct=YOUR_BILI_JCT
```

### 3. Configure SM.MS
```bash
.\pypicgo.bat config set --host smms --kv token=YOUR_SMMS_TOKEN
```

### 4. Set Default Host
To avoid typing `--host` every time:
```bash
.\pypicgo.bat config set --kv default_host=bilibili
```

## Usage

### CLI Usage

**Upload a file:**
```bash
.\pypicgo.bat upload "path/to/image.png"
```

**Upload with specific host:**
```bash
.\pypicgo.bat upload image.png --host github
```

**Upload and specify output format:**
```bash
.\pypicgo.bat upload image.png --format url
```
*Supported formats: `markdown` (default), `html`, `url`, `ubb`.*

**Check History:**
```bash
.\pypicgo.bat history list
```

### HTTP API Usage (For Typora/Obsidian)

Start the server:
```bash
python -m pypicgo.api.app
```
The server runs on `http://127.0.0.1:8765`.

**API Endpoint:** `POST http://127.0.0.1:8765/upload`

**Typora Configuration:**
1. Open Typora Preferences -> Image.
2. Select "Custom Command".
3. Command: `python -m pypicgo.cli.main upload` (Ensure python is in your PATH, or use absolute path to `pypicgo.bat`).

## Development

### Project Structure
- `pypicgo/core`: Core logic (Pipeline, Config, Events).
- `pypicgo/adapters`: Image host adapters (GitHub, Bilibili, etc.).
- `pypicgo/cli`: Command line interface.
- `pypicgo/api`: HTTP API server.

### Add New Adapter
Inherit from `UploaderAdapter` in `pypicgo/adapters/` and register it.

```python
from .base import UploaderAdapter, register_adapter

@register_adapter("myhost")
class MyHostAdapter(UploaderAdapter):
    def upload(self, files, config):
        # implementation
        return ["url"]
```
