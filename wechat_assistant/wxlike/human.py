"""拟人化行为：随机停顿、贝塞尔曲线鼠标移动、带抖动的点击、自然滚动。

设计目标：让点赞操作在"节奏 / 轨迹 / 停顿 / 概率"上尽量贴近真人，
避免出现机械、规律、秒赞等容易被风控识别的特征。
"""

from __future__ import annotations

import random
import time
from typing import Tuple

try:
    import pyautogui
    # 关闭 pyautogui 自带的固定延时，由我们自己控制节奏
    pyautogui.PAUSE = 0
    # 失败保护：鼠标移到屏幕左上角可紧急中断
    pyautogui.FAILSAFE = True
except Exception:  # pragma: no cover - 仅在非 Windows 环境导入失败时
    pyautogui = None

from .config import HumanCfg


class Human:
    def __init__(self, cfg: HumanCfg, dry_run: bool = True, logger=None):
        self.cfg = cfg
        self.dry_run = dry_run
        self.log = logger

    # ---------- 停顿 ----------
    def _sleep(self, lo: float, hi: float) -> None:
        time.sleep(random.uniform(lo, hi))

    def read_pause(self) -> None:
        """模拟阅读一条朋友圈的时间。"""
        self._sleep(self.cfg.read_delay_min, self.cfg.read_delay_max)

    def hesitate(self) -> None:
        """点击前的短暂犹豫。"""
        self._sleep(self.cfg.click_hesitation_min, self.cfg.click_hesitation_max)

    # ---------- 鼠标移动 ----------
    @staticmethod
    def _bezier_point(p0, p1, p2, p3, t):
        """三次贝塞尔曲线上的点。"""
        mt = 1 - t
        x = (mt**3) * p0[0] + 3 * (mt**2) * t * p1[0] + 3 * mt * (t**2) * p2[0] + (t**3) * p3[0]
        y = (mt**3) * p0[1] + 3 * (mt**2) * t * p1[1] + 3 * mt * (t**2) * p2[1] + (t**3) * p3[1]
        return x, y

    def move_to(self, x: int, y: int) -> None:
        """沿一条带随机控制点的贝塞尔曲线把鼠标移到目标，模拟手部轨迹。"""
        if self.dry_run or pyautogui is None:
            if self.log:
                self.log.debug(f"[dry-run] 移动鼠标 -> ({x}, {y})")
            return

        start = pyautogui.position()
        # 两个随机控制点，让轨迹有自然的弧度
        ctrl1 = (
            start[0] + random.uniform(-0.3, 0.5) * (x - start[0]),
            start[1] + random.uniform(-0.5, 0.5) * (y - start[1]),
        )
        ctrl2 = (
            x + random.uniform(-0.3, 0.3) * (x - start[0]),
            y + random.uniform(-0.3, 0.3) * (y - start[1]),
        )

        steps = random.randint(self.cfg.mouse_move_steps_min, self.cfg.mouse_move_steps_max)
        for i in range(1, steps + 1):
            t = i / steps
            px, py = self._bezier_point(start, ctrl1, ctrl2, (x, y), t)
            pyautogui.moveTo(px, py)
            self._sleep(self.cfg.mouse_step_delay_min, self.cfg.mouse_step_delay_max)

    def click(self, x: int, y: int) -> None:
        """带热区抖动地移动并点击。"""
        jitter = self.cfg.click_jitter_px
        tx = x + random.randint(-jitter, jitter)
        ty = y + random.randint(-jitter, jitter)

        self.move_to(tx, ty)
        self.hesitate()

        if self.dry_run or pyautogui is None:
            if self.log:
                self.log.info(f"[dry-run] 点击 ({tx}, {ty})")
            return
        pyautogui.click(tx, ty)

    # ---------- 滚动 ----------
    def scroll_down(self) -> None:
        """向下滚动浏览，滚动量与停顿随机。"""
        ticks = random.randint(self.cfg.scroll_ticks_min, self.cfg.scroll_ticks_max)
        if self.dry_run or pyautogui is None:
            if self.log:
                self.log.debug(f"[dry-run] 向下滚动 {ticks} 档")
        else:
            # 分多次小滚动，比一次性滚动更自然
            for _ in range(ticks):
                pyautogui.scroll(-random.randint(100, 220))
                self._sleep(0.05, 0.2)
        self._sleep(self.cfg.scroll_pause_min, self.cfg.scroll_pause_max)

    # ---------- 概率决策 ----------
    def should_like(self) -> bool:
        """按配置的点赞率随机决定本条是否点赞。"""
        return random.random() < self.cfg.like_probability
