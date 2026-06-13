"""安全频控：速率上限、定时休息、活跃时段、连续失败熔断。"""

from __future__ import annotations

import random
import time
from datetime import datetime

from .config import SafetyCfg


class SafetyGuard:
    def __init__(self, cfg: SafetyCfg, dry_run: bool = True, logger=None):
        self.cfg = cfg
        self.dry_run = dry_run
        self.log = logger
        self.likes = 0
        self.posts = 0
        self.consecutive_failures = 0

    # ---------- 运行前检查 ----------
    def check_active_hours(self) -> bool:
        start = self.cfg.active_hours_start
        end = self.cfg.active_hours_end
        if start is None or end is None:
            return True
        hour = datetime.now().hour
        ok = start <= hour < end
        if not ok and self.log:
            self.log.warning(
                f"当前 {hour} 点不在活跃时段 [{start}, {end})，拒绝运行。"
            )
        return ok

    # ---------- 计数与上限 ----------
    def can_continue(self) -> bool:
        """是否还能继续处理下一条。"""
        if self.posts >= self.cfg.max_posts_per_run:
            self._stop("已达单次处理条数上限")
            return False
        if self.likes >= self.cfg.max_likes_per_run:
            self._stop("已达单次点赞次数上限")
            return False
        if self.consecutive_failures >= self.cfg.max_consecutive_failures:
            self._stop("连续失败过多，触发熔断")
            return False
        return True

    def _stop(self, reason: str) -> None:
        if self.log:
            self.log.info(f"停止：{reason}（已处理 {self.posts} 条 / 点赞 {self.likes} 次）")

    def record_post(self) -> None:
        self.posts += 1

    def record_like(self) -> None:
        self.likes += 1
        self.consecutive_failures = 0
        # 达到休息阈值则休息
        if self.cfg.rest_after_likes > 0 and self.likes % self.cfg.rest_after_likes == 0:
            self._rest()

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.log:
            self.log.warning(f"操作失败（连续 {self.consecutive_failures} 次）")

    def record_skip(self) -> None:
        """跳过不计入失败。"""
        self.consecutive_failures = 0

    def _rest(self) -> None:
        secs = random.uniform(self.cfg.rest_seconds_min, self.cfg.rest_seconds_max)
        if self.log:
            self.log.info(f"已点赞 {self.likes} 次，休息 {secs:.0f} 秒……")
        if not self.dry_run:
            time.sleep(secs)

    def summary(self) -> str:
        return f"本次处理 {self.posts} 条，点赞 {self.likes} 次。"
