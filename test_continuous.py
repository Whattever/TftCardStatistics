#!/usr/bin/env python3
"""
测试持续监控模式的简单脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import run_fixed_regions_matching

def test_fixed_regions_matching():
    """测试固定区域模板匹配功能"""
    print("=== 测试固定区域模板匹配功能 ===")
    
    try:
        # 测试核心功能
        result = run_fixed_regions_matching(
            templates_dir="tft_units",
            monitor_index=1,
            threshold=0.8,
            show=False
        )
        
        print(f"\n测试完成！匹配结果: {result}")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_regions_matching()
    if success:
        print("\n✅ 测试通过！持续监控模式的核心功能正常工作。")
    else:
        print("\n❌ 测试失败！请检查错误信息。")
    
    print("\n现在可以运行持续监控模式:")
    print("python run.py --continuous")
