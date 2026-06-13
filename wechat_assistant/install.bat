@echo off
chcp 65001 >nul
REM ============================================================
REM  微信朋友圈自动点赞助手 - 一键安装 (Windows)
REM  双击本文件即可安装依赖
REM ============================================================
echo.
echo ====== 微信朋友圈自动点赞助手 · 安装 ======
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python。
    echo 请先到 https://www.python.org/downloads/ 下载安装 Python 3.9 以上版本，
    echo 安装时务必勾选 "Add Python to PATH"，然后重新运行本脚本。
    echo.
    pause
    exit /b 1
)

echo [1/2] 检测到 Python：
python --version

echo.
echo [2/2] 正在安装依赖（首次较慢，请耐心等待）……
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败，请检查网络后重试。
    pause
    exit /b 1
)

echo.
echo ====== 安装完成！ ======
echo 下一步：双击 start.bat 先进行"干跑"测试（不会真正点击）。
echo.
pause
