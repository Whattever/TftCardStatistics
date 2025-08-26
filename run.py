#!/usr/bin/env python3
"""
TFT Card Statistics 启动脚本
使用方式: python run.py [参数]
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行main函数
from src.main import main

if __name__ == "__main__":
    main()
