# 微信朋友圈自动点赞助手

PC 微信（Windows）朋友圈自动点赞工具，模拟真人行为逐条点赞。
这是「微信助手客户管理软件」方案的**第一个功能**。

> ⚠️ **重要提示**：自动化操作微信可能违反微信用户协议，存在**账号被限制或封禁**的风险。
> 本工具仅供个人在知情并自担风险的前提下使用。请务必先用 `dry-run` 模式调试，
> 控制频率、尊重好友，不要用于骚扰。

---

## 运行环境

- **操作系统**：Windows（依赖 Windows UI Automation，无法在 Linux/Mac 运行）
- **Python**：3.9+
- **微信**：PC 版（需为**带朋友圈功能**的新版微信电脑端）

## 安装

```bash
cd wechat_assistant
pip install -r requirements.txt
```

## 配置

编辑 `config.yaml`，重点关注：

- `wechat.exe_path`：你电脑上微信的安装路径
- `human.like_probability`：点赞率（0~1），真人不会条条都赞
- `safety.max_likes_per_run` / `rest_after_likes`：频控与休息
- `safety.active_hours_*`：只在活跃时段运行
- `runtime.dry_run`：**默认 true**，只模拟不真正点击

## 使用步骤（建议顺序）

1. **先扫码登录** PC 微信。

2. **干跑调试**（不会真正点击，只打日志，安全）：
   ```bash
   python run.py
   ```

3. **检查控件**（如果定位不到朋友圈/点赞按钮，用它打印控件树，
   按实际控件名调整 `wxlike/moments.py` 顶部的文案常量）：
   ```bash
   # 先手动打开微信朋友圈窗口，再运行：
   python run.py --inspect
   ```

4. **确认无误后实际执行**：
   ```bash
   python run.py --live
   ```

> 紧急停止：把鼠标快速甩到屏幕**左上角**会触发 pyautogui 的 FAILSAFE 中断；
> 或在终端按 `Ctrl+C`。

## 项目结构

```
wechat_assistant/
├── run.py              # 命令行入口（含 --inspect 调试）
├── config.yaml         # 所有拟人化 / 频控参数
├── requirements.txt
└── wxlike/
    ├── config.py       # 配置加载
    ├── logger.py       # 日志
    ├── human.py        # 拟人化：随机停顿 / 贝塞尔鼠标 / 抖动点击 / 滚动
    ├── safety.py       # 频控：上限 / 休息 / 活跃时段 / 熔断
    ├── wechat.py       # 启动微信 + 进入朋友圈
    ├── moments.py      # 逐条识别 / 判断已赞 / 点赞主循环
    └── main.py         # 编排
```

## 工作流程

```
启动微信 → 进入朋友圈 → 逐条:
   "阅读"停顿 → 按概率决定是否赞 → 打开"···"菜单
   → 判断是否已赞(是则跳过) → 点"赞" → 计数/频控
→ 滚动加载下一屏 → 直到上限/到底/熔断
```

## 已知限制 / 待打磨

- 不同微信版本控件名可能不同，`moments.py` 顶部的文案常量与
  `wechat.py` 的入口定位可能需要按 `--inspect` 结果微调。
- "已赞"判断目前依赖菜单中是否出现「取消」，建议先在小号验证准确性。
- 图像模板兜底（`templates/`）尚未启用，后续可加入按钮截图做模板匹配。
- 本工具**未在本仓库的 CI/云端环境实测**（无 Windows GUI），需在你本机验证。
