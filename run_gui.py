#!/usr/bin/env python3
"""
TFT卡牌统计GUI启动脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gui import main
    print("正在启动TFT卡牌统计GUI...")
    main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包")
    print("运行: pip install -r requirements.txt")
except Exception as e:
    print(f"启动错误: {e}")
    import traceback
    traceback.print_exc()
