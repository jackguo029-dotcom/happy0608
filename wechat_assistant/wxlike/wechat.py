"""微信启动与导航：自动打开 PC 微信、进入朋友圈、拿到朋友圈窗口。

依赖 Windows UI Automation（uiautomation 库）。该库通过控件树定位元素，
比纯坐标点击稳定。但微信不同版本控件命名可能有差异，因此关键控件名
都集中可改，并提供图像兜底（见 moments.py）。
"""

from __future__ import annotations

import os
import subprocess
import time

try:
    import uiautomation as auto
except Exception:  # pragma: no cover - 非 Windows 环境
    auto = None

from .config import WeChatCfg


class WeChatNavigator:
    def __init__(self, cfg: WeChatCfg, logger=None):
        self.cfg = cfg
        self.log = logger
        self.main_window = None
        self.moments_window = None

    def _require_uia(self):
        if auto is None:
            raise RuntimeError(
                "未能加载 uiautomation。请在 Windows 上运行并安装依赖："
                "pip install uiautomation"
            )

    # ---------- 启动微信 ----------
    def ensure_running(self) -> bool:
        """确保微信主窗口存在；若未运行则尝试启动。"""
        self._require_uia()

        win = auto.WindowControl(searchDepth=1, Name=self.cfg.main_window_title)
        if win.Exists(maxSearchSeconds=2):
            self.main_window = win
            if self.log:
                self.log.info("检测到微信已在运行。")
            return True

        # 未运行：尝试启动 exe
        if not os.path.exists(self.cfg.exe_path):
            if self.log:
                self.log.error(f"微信可执行文件不存在：{self.cfg.exe_path}")
            return False

        if self.log:
            self.log.info("微信未运行，正在启动……")
        subprocess.Popen([self.cfg.exe_path])

        # 等待主窗口出现（登录可能需要手动扫码）
        deadline = time.time() + self.cfg.launch_timeout
        while time.time() < deadline:
            if win.Exists(maxSearchSeconds=2):
                self.main_window = win
                if self.log:
                    self.log.info("微信主窗口已就绪。")
                return True
            time.sleep(1)

        if self.log:
            self.log.error("等待微信主窗口超时（可能需要先手动登录）。")
        return False

    # ---------- 进入朋友圈 ----------
    def open_moments(self) -> bool:
        """点击主窗口侧边栏「朋友圈」入口，打开朋友圈窗口。

        微信 PC 版侧边栏的朋友圈通常是一个工具按钮，常见 Name 包括
        「朋友圈」。先尝试按钮，再回退到菜单项查找。
        """
        self._require_uia()
        if self.main_window is None:
            if self.log:
                self.log.error("主窗口未初始化，无法打开朋友圈。")
            return False

        self.main_window.SetActive()
        time.sleep(0.5)

        # 1) 直接找名为「朋友圈」的按钮
        btn = self.main_window.ButtonControl(Name=self.cfg.moments_window_title)
        if btn.Exists(maxSearchSeconds=3):
            btn.Click(simulateMove=True)
        else:
            # 2) 回退：在整个主窗口里找含「朋友圈」的可点击控件
            ctrl = self.main_window.Control(searchDepth=20, Name=self.cfg.moments_window_title)
            if ctrl.Exists(maxSearchSeconds=3):
                ctrl.Click(simulateMove=True)
            else:
                if self.log:
                    self.log.error("未找到「朋友圈」入口，请检查微信版本/控件名。")
                return False

        # 等待朋友圈独立窗口出现
        moments = auto.WindowControl(searchDepth=1, Name=self.cfg.moments_window_title)
        if moments.Exists(maxSearchSeconds=8):
            self.moments_window = moments
            self.moments_window.SetActive()
            if self.log:
                self.log.info("已进入朋友圈窗口。")
            time.sleep(1.5)  # 等信息流加载
            return True

        if self.log:
            self.log.error("朋友圈窗口未出现。")
        return False

    def moments_rect(self):
        """返回朋友圈窗口的矩形区域（left, top, right, bottom）。"""
        if self.moments_window is None:
            return None
        r = self.moments_window.BoundingRectangle
        return (r.left, r.top, r.right, r.bottom)
