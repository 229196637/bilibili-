from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# Allow running directly from source
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parents[2]))
    __package__ = "pypicgo.cli"

from ..core import PicGoCore


def cmd_upload(args: argparse.Namespace) -> int:
    core = PicGoCore()
    files: List[str] = []
    for p in args.files:
        if Path(p).is_file():
            files.append(p)
    if not files:
        print("no files found")
        return 1
    try:
        out = core.run(files, host=args.host, fmt=args.format)
        print(out)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        if "requires repo and token" in str(e):
            print("\nPlease configure GitHub token and repo:")
            print("  python -m pypicgo.cli.main config set --host github --kv token=YOUR_TOKEN repo=USER/REPO")
        elif "requires token" in str(e):
            print("\nPlease configure token:")
            print(f"  python -m pypicgo.cli.main config set --host {args.host or 'smms'} --kv token=YOUR_TOKEN")
        elif "requires sessdata" in str(e):
            print("\nPlease configure Bilibili sessdata and bili_jct:")
            print("  python -m pypicgo.cli.main config set --host bilibili --kv sessdata=YOUR_SESSDATA bili_jct=YOUR_BILI_JCT")
        return 1


def cmd_config(args: argparse.Namespace) -> int:
    core = PicGoCore()
    if args.action == "get":
        if args.host:
            print(core.config.get_host_config(args.host))
        else:
            print(core.config.data)
        return 0
    if args.action == "set":
        kv = dict(item.split("=", 1) for item in args.kv)
        if args.host:
            core.config.set_host_config(args.host, kv)
        else:
            core.config.set_global_config(kv)
        print("ok")
        return 0
    print("unknown action")
    return 1


def cmd_history(args: argparse.Namespace) -> int:
    core = PicGoCore()
    if args.action == "list":
        for item in core.history.list():
            print(item)
        return 0
    if args.action == "clear":
        core.history.clear()
        print("ok")
        return 0
    print("unknown action")
    return 1


def cmd_plugin(args: argparse.Namespace) -> int:
    # 占位：插件系统后续实现
    print("plugin system not implemented yet")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pypicgo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_upload = sub.add_parser("upload", help="upload files")
    p_upload.add_argument("files", nargs="+", help="file paths")
    p_upload.add_argument("--host", default=None, help="image host")
    p_upload.add_argument("--format", default=None, help="output format")
    p_upload.set_defaults(func=cmd_upload)

    p_config = sub.add_parser("config", help="get/set config")
    p_config.add_argument("action", choices=["get", "set"])
    p_config.add_argument("--host", default=None)
    p_config.add_argument("--kv", nargs="*", default=[])
    p_config.set_defaults(func=cmd_config)

    p_history = sub.add_parser("history", help="history ops")
    p_history.add_argument("action", choices=["list", "clear"])
    p_history.set_defaults(func=cmd_history)

    p_plugin = sub.add_parser("plugin", help="plugin ops")
    p_plugin.add_argument("action", choices=["list", "install", "remove"])
    p_plugin.set_defaults(func=cmd_plugin)

    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    sys.exit(main())

