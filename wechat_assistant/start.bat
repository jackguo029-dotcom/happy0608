@echo off
chcp 65001 >nul
REM ============================================================
REM  微信朋友圈自动点赞助手 - 启动菜单 (Windows)
REM ============================================================
:menu
cls
echo.
echo ========== 微信朋友圈自动点赞助手 ==========
echo.
echo  请先确保 PC 微信已扫码登录！
echo.
echo   [1] 干跑测试（只打日志，不真正点击，安全）
echo   [2] 实际执行（真正点赞，请先确认配置）
echo   [3] 调试：打印朋友圈控件树（需先手动打开朋友圈）
echo   [4] 退出
echo.
set /p choice=请输入数字后回车：

if "%choice%"=="1" (
    python run.py
    pause
    goto menu
)
if "%choice%"=="2" (
    echo.
    echo [警告] 即将真正执行点赞，请确认已用干跑测试验证过！
    set /p confirm=确定继续请输入 yes：
    if /i "%confirm%"=="yes" (
        python run.py --live
    )
    pause
    goto menu
)
if "%choice%"=="3" (
    python run.py --inspect
    pause
    goto menu
)
if "%choice%"=="4" exit /b 0

goto menu
