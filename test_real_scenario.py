#!/usr/bin/env python3
"""
真实场景OCR记忆功能测试
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def test_real_scenario():
    """测试真实场景下的OCR记忆功能"""
    print("=== 真实场景OCR记忆测试 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 初始状态")
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n2. 第一次OCR识别成功（数字8）")
    # 模拟OCR识别成功，识别出数字8
    ocr.last_recognized_number = 8
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n3. 第二次OCR识别失败")
    # 模拟OCR识别失败，返回空字符串
    print("   模拟：OCR返回空字符串")
    
    # 直接调用OCR的识别方法，模拟识别失败
    # 创建一个无法识别的图像
    noise_img = np.random.randint(0, 30, (50, 30), dtype=np.uint8)
    result = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    if result == 8:
        print("   ✅ 正确延用了上次结果: 8")
    else:
        print(f"   ❌ 错误：期望延用8，实际得到{result}")
    
    print("\n4. 第三次OCR识别失败")
    # 再次模拟OCR识别失败
    result = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    if result == 8:
        print("   ✅ 正确延用了上次结果: 8")
    else:
        print(f"   ❌ 错误：期望延用8，实际得到{result}")
    
    print("\n5. 第四次OCR识别成功（数字3）")
    # 模拟OCR识别成功，识别出数字3
    ocr.last_recognized_number = 3
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n6. 第五次OCR识别失败")
    # 再次模拟OCR识别失败
    result = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    if result == 3:
        print("   ✅ 正确延用了上次结果: 3")
    else:
        print(f"   ❌ 错误：期望延用3，实际得到{result}")

def test_exception_scenario():
    """测试异常情况下的OCR记忆功能"""
    print("\n=== 异常情况OCR记忆测试 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 设置记忆值为8")
    ocr.last_recognized_number = 8
    print(f"   记忆值: {ocr.last_recognized_number}")
    
    print("\n2. 模拟OCR异常情况")
    try:
        # 模拟一个异常
        raise Exception("模拟OCR异常")
    except Exception as e:
        print(f"   捕获异常: {e}")
        # 使用OCR模块的回退机制
        fallback_number = ocr._get_fallback_number()
        print(f"   回退值: {fallback_number}")
        
        if fallback_number == 8:
            print("   ✅ 正确延用了上次结果: 8")
        else:
            print(f"   ❌ 错误：期望8，实际{fallback_number}")

if __name__ == "__main__":
    test_real_scenario()
    test_exception_scenario()
    
    print("\n=== 测试总结 ===")
    print("这个测试模拟了真实使用场景：")
    print("1. OCR成功识别数字8")
    print("2. OCR识别失败时应该延用8")
    print("3. OCR再次成功识别数字3")
    print("4. OCR识别失败时应该延用3")
    print("5. 异常情况下也应该延用上次结果")
