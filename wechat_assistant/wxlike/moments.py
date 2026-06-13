"""朋友圈信息流处理：逐条识别、判断是否已赞、执行点赞。

PC 微信朋友圈每条动态右下角有一个「···」操作按钮，点击后弹出
浮层菜单，内含「赞 / 评论」；若该条已点过赞，则菜单显示「取消 / 评论」。
我们据此判断点赞状态，避免误取消已点的赞。

主路径用 uiautomation 遍历控件；当控件识别失败时，可切换到
image 兜底（模板匹配，见 vision.py）。
"""

from __future__ import annotations

import time
from typing import List

try:
    import uiautomation as auto
except Exception:  # pragma: no cover
    auto = None

from .human import Human
from .safety import SafetyGuard


# 不同微信版本里这些文案可能不同，集中在此便于调整
MENU_BUTTON_NAMES = ("···", "…", "操作")     # 每条动态的"···"按钮
LIKE_TEXTS = ("赞", "点赞", "Like")
UNLIKE_TEXTS = ("取消", "Cancel")            # 已赞后菜单里的"取消"


class MomentsLiker:
    def __init__(self, moments_window, human: Human, guard: SafetyGuard, logger=None):
        self.win = moments_window
        self.human = human
        self.guard = guard
        self.log = logger
        # 记录已处理过的动态指纹，避免滚动时重复处理同一条
        self._seen = set()

    # ---------- 找出当前可见的动态条目 ----------
    def _visible_posts(self) -> List["auto.Control"]:
        """返回当前窗口内可见的动态条目控件列表。

        朋友圈列表通常是一个 List/Pane，子节点为每条动态。这里取列表下
        的直接子项；不同版本结构不同，必要时调整 searchDepth 与类型。
        """
        posts = []
        # 朋友圈内容区一般是个可滚动的 List
        container = self.win.ListControl()
        if not container.Exists(maxSearchSeconds=2):
            container = self.win  # 回退：直接在窗口里找

        for child in container.GetChildren():
            rect = child.BoundingRectangle
            # 过滤掉高度过小的非动态控件（分隔条等）
            if rect.height() < 40:
                continue
            posts.append(child)
        return posts

    def _fingerprint(self, post) -> str:
        """为一条动态生成简单指纹（取其文本+位置），用于去重。"""
        try:
            text = post.Name or ""
            return f"{text[:40]}@{post.BoundingRectangle.top}"
        except Exception:
            return str(id(post))

    # ---------- 处理单条动态 ----------
    def _find_menu_button(self, post):
        """在一条动态内找到「···」操作按钮。"""
        for name in MENU_BUTTON_NAMES:
            btn = post.ButtonControl(Name=name)
            if btn.Exists(maxSearchSeconds=1):
                return btn
        # 回退：找该条目内的任意 Button（通常"···"是唯一按钮）
        for child in post.GetChildren():
            if child.ControlTypeName == "ButtonControl":
                return child
        return None

    def _popup_menu(self):
        """获取「···」点击后弹出的浮层菜单控件。"""
        # 浮层通常是一个独立的小 Window/Pane，包含"赞""评论"
        for texts in (LIKE_TEXTS, UNLIKE_TEXTS):
            for t in texts:
                ctrl = auto.TextControl(searchDepth=12, Name=t)
                if ctrl.Exists(maxSearchSeconds=1):
                    return ctrl
        return None

    def _is_already_liked(self) -> bool:
        """根据浮层菜单是否出现「取消」判断该条是否已点赞。"""
        for t in UNLIKE_TEXTS:
            if auto.TextControl(searchDepth=12, Name=t).Exists(maxSearchSeconds=1):
                return True
        return False

    def _click_like_in_menu(self) -> bool:
        """在浮层菜单里点击「赞」。"""
        for t in LIKE_TEXTS:
            like_btn = auto.Control(searchDepth=12, Name=t)
            if like_btn.Exists(maxSearchSeconds=1):
                r = like_btn.BoundingRectangle
                cx = (r.left + r.right) // 2
                cy = (r.top + r.bottom) // 2
                self.human.click(cx, cy)
                return True
        return False

    def _close_menu(self):
        """点击空白处关闭浮层菜单（避免误触）。"""
        try:
            r = self.win.BoundingRectangle
            # 点击窗口左上角空白区
            self.human.click(r.left + 30, r.top + 80)
        except Exception:
            pass

    def process_post(self, post) -> str:
        """处理一条动态，返回结果：liked / skipped / already / failed。"""
        # 1) 拟人化：先"阅读"
        self.human.read_pause()

        # 2) 概率决定是否点赞
        if not self.human.should_like():
            if self.log:
                self.log.info("按点赞率随机跳过本条。")
            return "skipped"

        # 3) 打开"···"菜单
        menu_btn = self._find_menu_button(post)
        if menu_btn is None:
            if self.log:
                self.log.warning("未找到本条的「···」按钮，跳过。")
            return "failed"

        r = menu_btn.BoundingRectangle
        self.human.click((r.left + r.right) // 2, (r.top + r.bottom) // 2)
        time.sleep(0.6)  # 等浮层弹出

        # 4) 已赞则不重复
        if self._is_already_liked():
            if self.log:
                self.log.info("本条已点赞，跳过。")
            self._close_menu()
            return "already"

        # 5) 点击"赞"
        ok = self._click_like_in_menu()
        if ok:
            if self.log:
                self.log.info("✓ 已点赞。")
            return "liked"

        self._close_menu()
        return "failed"

    # ---------- 主循环 ----------
    def run(self) -> None:
        if self.log:
            self.log.info("开始处理朋友圈信息流……")

        while self.guard.can_continue():
            posts = self._visible_posts()
            new_in_view = 0

            for post in posts:
                if not self.guard.can_continue():
                    break
                fp = self._fingerprint(post)
                if fp in self._seen:
                    continue
                self._seen.add(fp)
                new_in_view += 1
                self.guard.record_post()

                result = self.process_post(post)
                if result == "liked":
                    self.guard.record_like()
                elif result == "failed":
                    self.guard.record_failure()
                else:  # skipped / already
                    self.guard.record_skip()

            # 本屏没有新动态了，向下滚动加载更多
            if new_in_view == 0:
                if self.log:
                    self.log.debug("当前屏无新动态，向下滚动。")
            self.human.scroll_down()

            # 滚动后若仍无新内容，认为到底了
            if new_in_view == 0 and not self._has_more_after_scroll():
                if self.log:
                    self.log.info("已到达信息流底部或无更多内容。")
                break

        if self.log:
            self.log.info(self.guard.summary())

    def _has_more_after_scroll(self) -> bool:
        """滚动后检查是否出现了之前没见过的动态。"""
        for post in self._visible_posts():
            if self._fingerprint(post) not in self._seen:
                return True
        return False
