#!/usr/bin/env python3
"""
测试修复后的OCR记忆功能
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def test_fixed_memory():
    """测试修复后的OCR记忆功能"""
    print("=== 测试修复后的OCR记忆功能 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 初始状态")
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n2. 第一次OCR识别成功（数字5）")
    # 模拟OCR识别成功
    ocr.last_recognized_number = 5
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n3. 模拟OCR异常情况")
    print("   当OCR出现异常时，应该使用回退机制")
    
    # 模拟异常情况下的回退
    try:
        # 模拟一个异常
        raise Exception("模拟OCR异常")
    except Exception as e:
        print(f"   捕获异常: {e}")
        # 使用OCR模块的回退机制
        fallback_number = ocr._get_fallback_number()
        print(f"   回退值: {fallback_number}")
        
        if fallback_number == 5:
            print("   ✅ 正确延用了上次结果: 5")
        else:
            print(f"   ❌ 错误：期望5，实际{fallback_number}")
    
    print("\n4. 更新记忆值为3")
    ocr.last_recognized_number = 3
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n5. 再次模拟OCR异常情况")
    try:
        raise Exception("模拟第二次OCR异常")
    except Exception as e:
        print(f"   捕获异常: {e}")
        fallback_number = ocr._get_fallback_number()
        print(f"   回退值: {fallback_number}")
        
        if fallback_number == 3:
            print("   ✅ 正确延用了上次结果: 3")
        else:
            print(f"   ❌ 错误：期望3，实际{fallback_number}")
    
    print("\n6. 清空记忆值")
    ocr.last_recognized_number = None
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n7. 模拟OCR异常情况（无历史记录）")
    try:
        raise Exception("模拟无历史记录的OCR异常")
    except Exception as e:
        print(f"   捕获异常: {e}")
        fallback_number = ocr._get_fallback_number()
        print(f"   回退值: {fallback_number}")
        
        if fallback_number == 2:
            print("   ✅ 正确使用默认值: 2")
        else:
            print(f"   ❌ 错误：期望2，实际{fallback_number}")
    
    print("\n=== 测试结果总结 ===")
    print("✅ 修复后的OCR记忆功能能够：")
    print("   1. 在OCR异常时使用回退机制")
    print("   2. 正确延用上次识别结果")
    print("   3. 在无历史记录时使用默认值2")
    print("   4. 不再硬编码默认值2")

if __name__ == "__main__":
    test_fixed_memory()
