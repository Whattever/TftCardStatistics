@echo off
echo TFT卡牌统计数据查看工具
echo ================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 运行统计查看工具
python stats_viewer.py %*

echo.
pause
