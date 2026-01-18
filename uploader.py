import json
import os
import requests
from urllib.parse import unquote

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"SESSDATA": "", "bili_jct": ""}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def upload_bilibili(image_bytes):
    cfg = load_config()
    sess_raw = cfg.get("SESSDATA") or ""
    csrf = cfg.get("bili_jct") or ""
    if not sess_raw or not csrf:
        raise Exception("SESSDATA or bili_jct missing")
    sess = unquote(sess_raw)
    cookies = {"SESSDATA": sess, "bili_jct": csrf}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://t.bilibili.com/",
        "Origin": "https://www.bilibili.com",
        "X-CSRF-TOKEN": csrf,
        "Accept": "application/json"
    }

    files = {"file": ("image.png", image_bytes, "image/png")}
    data = {"csrf": csrf, "csrf_token": csrf}

    url_new = "https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs"
    r = requests.post(url_new, data=data, files=files, headers=headers, cookies=cookies, timeout=30)
    ok = False
    if r.ok:
        j = r.json()
        if j.get("code") == 0:
            u = j["data"].get("image_url") or j["data"].get("url")
            if u and u.startswith("http://"):
                u = u.replace("http://", "https://")
            if u:
                return u
        else:
            ok = False
    else:
        ok = False

    headers_fallback = {
        "User-Agent": headers["User-Agent"],
        "Referer": "https://t.bilibili.com/",
        "Origin": "https://t.bilibili.com",
        "Accept": "application/json"
    }
    files_old = {"file_up": ("image.png", image_bytes, "image/png")}
    data_old = {"category": "daily", "biz": "draw", "csrf": csrf}
    url_old = "https://api.vc.bilibili.com/api/v1/draw/upload"
    r2 = requests.post(url_old, data=data_old, files=files_old, headers=headers_fallback, cookies=cookies, timeout=30)
    if not r2.ok:
        raise Exception(f"Upload failed: HTTP {r2.status_code}")
    j2 = r2.json()
    if j2.get("code") == 0:
        u = j2["data"]["img_src"]
        if u.startswith("http://"):
            u = u.replace("http://", "https://")
        return u
    raise Exception(f"Upload failed: {j2.get('message', 'unknown')}")
