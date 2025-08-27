@echo off
chcp 65001 >nul
echo 正在启动TFT卡牌统计GUI系统...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查依赖包
echo 检查依赖包...
pip show matplotlib >nul 2>&1
if errorlevel 1 (
    echo 正在安装matplotlib...
    pip install matplotlib
)

pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo 正在安装opencv-python...
    pip install opencv-python
)

pip show mss >nul 2>&1
if errorlevel 1 (
    echo 正在安装mss...
    pip install mss
)

pip show pynput >nul 2>&1
if errorlevel 1 (
    echo 正在安装pynput...
    pip install pynput
)

echo.
echo 启动GUI界面...
python gui_launcher.py

if errorlevel 1 (
    echo.
    echo GUI启动失败，请检查错误信息
    pause
)
