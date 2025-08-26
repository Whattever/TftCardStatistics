@echo off
echo 启动TFT卡牌统计持续监控模式...
echo.
echo 快捷键说明:
echo   D     - 触发截图和模板匹配
echo   Ctrl+F1 - 退出程序
echo.
echo 程序将持续运行，等待快捷键输入...
echo.
python run.py --continuous
pause
