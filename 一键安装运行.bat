@echo off
chcp 65001 >nul
setlocal
REM ============================================================
REM  微信朋友圈自动点赞助手 - 全自动一键脚本
REM  功能：自动下载代码 + 安装依赖 + 启动
REM  你只需要双击本文件即可
REM ============================================================

set REPO_ZIP=https://github.com/jackguo029-dotcom/happy0608/archive/refs/heads/claude/awesome-mayer-e9eqfy.zip
set WORKDIR=%USERPROFILE%\wechat-like-bot
set ZIPFILE=%WORKDIR%\repo.zip

echo.
echo ============================================
echo   微信朋友圈自动点赞助手 · 一键安装运行
echo ============================================
echo.

REM ---------- 1. 检查 Python ----------
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python。
    echo.
    echo 请先安装 Python（只需一次）：
    echo   1. 打开 https://www.python.org/downloads/
    echo   2. 下载 Python 3.9 以上版本
    echo   3. 安装时务必勾选 "Add Python to PATH"
    echo   4. 装完后重新双击本脚本
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [1/4] Python 已就绪：
python --version

REM ---------- 2. 下载代码 ----------
echo.
echo [2/4] 正在下载最新代码……
if not exist "%WORKDIR%" mkdir "%WORKDIR%"
powershell -Command "try { Invoke-WebRequest -Uri '%REPO_ZIP%' -OutFile '%ZIPFILE%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
    echo [错误] 下载失败。可能原因：网络问题，或仓库为私有需要登录。
    echo 解决办法：用浏览器打开仓库页面，切到分支 claude/awesome-mayer-e9eqfy，
    echo 点 Code -^> Download ZIP 手动下载解压后，直接运行里面的 install.bat。
    pause
    exit /b 1
)

REM ---------- 3. 解压 ----------
echo 正在解压……
powershell -Command "Expand-Archive -Path '%ZIPFILE%' -DestinationPath '%WORKDIR%' -Force"
set PROJDIR=%WORKDIR%\happy0608-claude-awesome-mayer-e9eqfy\wechat_assistant
if not exist "%PROJDIR%" (
    echo [错误] 解压后未找到项目目录，请手动检查 %WORKDIR%
    pause
    exit /b 1
)
cd /d "%PROJDIR%"

REM ---------- 4. 安装依赖 ----------
echo.
echo [3/4] 正在安装依赖（首次较慢）……
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络后重试。
    pause
    exit /b 1
)

REM ---------- 启动菜单 ----------
echo.
echo [4/4] 准备就绪！
:menu
echo.
echo ========== 请选择操作（先确保微信已登录）==========
echo   [1] 干跑测试（只打日志，不真正点击，建议先做）
echo   [2] 实际执行（真正点赞）
echo   [3] 调试：打印朋友圈控件树（需先手动打开朋友圈）
echo   [4] 退出
echo.
set /p choice=请输入数字后回车：
if "%choice%"=="1" ( python run.py & pause & goto menu )
if "%choice%"=="2" (
    set /p confirm=即将真正点赞，确认请输入 yes：
    if /i "!confirm!"=="yes" python run.py --live
    pause & goto menu
)
if "%choice%"=="3" ( python run.py --inspect & pause & goto menu )
if "%choice%"=="4" exit /b 0
goto menu
