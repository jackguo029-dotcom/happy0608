#!/usr/bin/env python
"""命令行入口。

用法：
    python run.py                 # 使用 config.yaml
    python run.py -c my.yaml       # 指定配置文件
    python run.py --live           # 关闭 dry-run，真正执行点赞
    python run.py --inspect        # 打印微信/朋友圈控件树，便于调试控件名
"""

from __future__ import annotations

import argparse
import sys

from wxlike.config import load_config
from wxlike.main import LikeBot


def cmd_inspect(cfg):
    """调试工具：打印朋友圈窗口的控件树，方便定位控件名。"""
    try:
        import uiautomation as auto
    except Exception:
        print("需在 Windows 上安装 uiautomation 才能使用 --inspect。")
        return 1

    win = auto.WindowControl(searchDepth=1, Name=cfg.wechat.moments_window_title)
    if not win.Exists(maxSearchSeconds=3):
        print(f"未找到「{cfg.wechat.moments_window_title}」窗口，请先手动打开朋友圈。")
        return 1
    print("朋友圈窗口控件树：")
    auto.EnumAndLogControl(win, maxDepth=8)
    return 0


def main():
    parser = argparse.ArgumentParser(description="微信朋友圈自动点赞助手")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--live", action="store_true", help="关闭 dry-run，真正执行")
    parser.add_argument("--inspect", action="store_true", help="打印控件树用于调试")
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.inspect:
        return cmd_inspect(cfg)

    if args.live:
        cfg.runtime.dry_run = False

    return LikeBot(cfg).run()


if __name__ == "__main__":
    sys.exit(main())
