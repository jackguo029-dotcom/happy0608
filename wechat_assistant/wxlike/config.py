"""配置加载：把 config.yaml 读成带默认值的结构化对象。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class WeChatCfg:
    exe_path: str = r"C:\Program Files\Tencent\WeChat\WeChat.exe"
    main_window_title: str = "微信"
    moments_window_title: str = "朋友圈"
    launch_timeout: int = 30


@dataclass
class HumanCfg:
    like_probability: float = 0.7
    read_delay_min: float = 1.5
    read_delay_max: float = 6.0
    click_hesitation_min: float = 0.3
    click_hesitation_max: float = 1.2
    mouse_move_steps_min: int = 25
    mouse_move_steps_max: int = 60
    mouse_step_delay_min: float = 0.004
    mouse_step_delay_max: float = 0.012
    click_jitter_px: int = 4
    scroll_ticks_min: int = 2
    scroll_ticks_max: int = 5
    scroll_pause_min: float = 0.8
    scroll_pause_max: float = 2.5


@dataclass
class SafetyCfg:
    max_posts_per_run: int = 50
    max_likes_per_run: int = 30
    rest_after_likes: int = 10
    rest_seconds_min: float = 30
    rest_seconds_max: float = 90
    active_hours_start: Optional[int] = 8
    active_hours_end: Optional[int] = 23
    max_consecutive_failures: int = 5


@dataclass
class RuntimeCfg:
    dry_run: bool = True
    log_level: str = "INFO"
    templates_dir: str = "templates"


@dataclass
class Config:
    wechat: WeChatCfg = field(default_factory=WeChatCfg)
    human: HumanCfg = field(default_factory=HumanCfg)
    safety: SafetyCfg = field(default_factory=SafetyCfg)
    runtime: RuntimeCfg = field(default_factory=RuntimeCfg)


def _merge(dc, data: dict):
    """把 dict 里的字段覆盖到 dataclass 上（只覆盖已知字段）。"""
    if not data:
        return dc
    for key, value in data.items():
        if hasattr(dc, key):
            setattr(dc, key, value)
    return dc


def load_config(path: str = "config.yaml") -> Config:
    cfg = Config()
    if not os.path.exists(path):
        # 没有配置文件就用全默认值
        return cfg

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    _merge(cfg.wechat, raw.get("wechat"))
    _merge(cfg.human, raw.get("human"))
    _merge(cfg.safety, raw.get("safety"))
    _merge(cfg.runtime, raw.get("runtime"))
    return cfg
