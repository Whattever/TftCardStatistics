@echo off
echo 自动截取FIXED_REGIONS区域图片并去重保存
echo.
cd /d "%~dp0\.."
python tools\auto_capture.py
pause
