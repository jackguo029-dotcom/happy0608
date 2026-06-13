"""编排层：把启动、导航、安全、拟人化、点赞串起来。"""

from __future__ import annotations

from .config import Config, load_config
from .human import Human
from .logger import get_logger
from .moments import MomentsLiker
from .safety import SafetyGuard
from .wechat import WeChatNavigator


class LikeBot:
    def __init__(self, config: Config):
        self.cfg = config
        self.log = get_logger(config.runtime.log_level)
        self.dry_run = config.runtime.dry_run

    def run(self) -> int:
        self.log.info("=" * 50)
        self.log.info("微信朋友圈自动点赞助手启动")
        self.log.info(f"模式：{'DRY-RUN（仅模拟，不真正点击）' if self.dry_run else '实际执行'}")
        self.log.info("=" * 50)

        guard = SafetyGuard(self.cfg.safety, self.dry_run, self.log)

        # 1) 活跃时段检查
        if not guard.check_active_hours():
            return 1

        # 2) 启动并定位微信
        nav = WeChatNavigator(self.cfg.wechat, self.log)
        try:
            if not nav.ensure_running():
                self.log.error("微信未就绪，退出。")
                return 1

            # 3) 进入朋友圈
            if not nav.open_moments():
                self.log.error("无法进入朋友圈，退出。")
                return 1

            # 4) 逐条点赞
            human = Human(self.cfg.human, self.dry_run, self.log)
            liker = MomentsLiker(nav.moments_window, human, guard, self.log)
            liker.run()

        except KeyboardInterrupt:
            self.log.warning("收到中断信号，停止。")
        except Exception as e:  # noqa: BLE001
            self.log.exception(f"运行出错：{e}")
            return 1

        self.log.info("=" * 50)
        self.log.info(guard.summary())
        self.log.info("结束。")
        return 0


def main(config_path: str = "config.yaml") -> int:
    cfg = load_config(config_path)
    return LikeBot(cfg).run()
