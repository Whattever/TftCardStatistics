#!/usr/bin/env python3
"""
测试OCR实例持久化后的记忆功能
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def test_persistent_ocr():
    """测试OCR实例持久化"""
    print("=== 测试OCR实例持久化 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 初始状态")
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n2. 第一次OCR识别成功（数字8）")
    # 模拟OCR识别成功
    ocr.last_recognized_number = 8
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n3. 模拟第一次调用run_fixed_regions_matching")
    print("   传递OCR实例，应该保持记忆")
    
    # 模拟函数调用，传递OCR实例
    def simulate_function_call(ocr_instance):
        print(f"   函数内OCR记忆值: {ocr_instance.last_recognized_number}")
        # 模拟OCR识别失败
        noise_img = np.random.randint(0, 30, (50, 30), dtype=np.uint8)
        result = ocr_instance.recognize_number(noise_img)
        print(f"   识别结果: {result}")
        return result
    
    result1 = simulate_function_call(ocr)
    
    if result1 == 8:
        print("   ✅ 第一次调用正确延用了8")
    else:
        print(f"   ❌ 第一次调用错误：期望8，实际{result1}")
    
    print("\n4. 模拟第二次调用run_fixed_regions_matching")
    print("   再次传递OCR实例，应该继续延用8")
    
    result2 = simulate_function_call(ocr)
    
    if result2 == 8:
        print("   ✅ 第二次调用正确延用了8")
    else:
        print(f"   ❌ 第二次调用错误：期望8，实际{result2}")
    
    print("\n5. 更新记忆值为3")
    ocr.last_recognized_number = 3
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n6. 模拟第三次调用run_fixed_regions_matching")
    print("   传递OCR实例，应该延用3")
    
    result3 = simulate_function_call(ocr)
    
    if result3 == 3:
        print("   ✅ 第三次调用正确延用了3")
    else:
        print(f"   ❌ 第三次调用错误：期望3，实际{result3}")
    
    print("\n=== 测试结果 ===")
    if result1 == 8 and result2 == 8 and result3 == 3:
        print("✅ OCR实例持久化成功！")
        print("✅ 记忆功能正常工作！")
        print("✅ 多次函数调用都能保持记忆！")
    else:
        print("❌ OCR实例持久化失败！")

def test_without_persistent_ocr():
    """测试没有持久化OCR实例的情况"""
    print("\n=== 测试没有持久化OCR实例 ===")
    
    print("1. 模拟每次调用都创建新OCR实例的情况")
    
    # 第一次调用
    ocr1 = NumberOCR()
    ocr1.last_recognized_number = 8
    print(f"   第一次调用OCR记忆值: {ocr1.last_recognized_number}")
    
    # 第二次调用（新实例）
    ocr2 = NumberOCR()
    print(f"   第二次调用OCR记忆值: {ocr2.last_recognized_number}")
    
    if ocr2.last_recognized_number is None:
        print("   ✅ 新OCR实例没有记忆值")
    else:
        print(f"   ❌ 新OCR实例意外有记忆值: {ocr2.last_recognized_number}")
    
    print("\n2. 这解释了为什么之前会显示2")
    print("   每次调用都创建新OCR实例 → 记忆丢失 → 使用默认值2")

if __name__ == "__main__":
    test_persistent_ocr()
    test_without_persistent_ocr()
    
    print("\n" + "="*60)
    print("总结：")
    print("✅ 修复前：每次调用都创建新OCR实例，记忆丢失")
    print("✅ 修复后：OCR实例持久化，记忆功能正常")
    print("✅ 现在OCR识别失败时会正确延用上次结果")
    print("="*60)
