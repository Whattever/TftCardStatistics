#!/usr/bin/env python3
"""
简单的OCR记忆功能测试
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def test_simple_memory():
    """简单测试OCR记忆功能"""
    print("=== 简单OCR记忆测试 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 创建OCR实例")
    print(f"   初始记忆值: {ocr.last_recognized_number}")
    
    print("\n2. 第一次识别数字 '5'")
    # 创建一个简单的数字5图像
    img5 = np.zeros((50, 30), dtype=np.uint8)
    cv2.putText(img5, "5", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 255, 2)
    result1 = ocr.recognize_number(img5)
    print(f"   识别结果: {result1}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n3. 第二次识别数字 '3'")
    # 创建一个简单的数字3图像
    img3 = np.zeros((50, 30), dtype=np.uint8)
    cv2.putText(img3, "3", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 255, 2)
    result2 = ocr.recognize_number(img3)
    print(f"   识别结果: {result2}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n4. 第三次识别无法识别的图像（应该延用上次结果 '3'）")
    # 创建一个无法识别的图像 - 使用噪点而不是纯黑
    noise_img = np.random.randint(0, 50, (50, 30), dtype=np.uint8)
    result3 = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result3}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n5. 第四次识别无法识别的图像（应该延用上次结果 '3'）")
    result4 = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result4}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n=== 测试结果 ===")
    if result1 == 5 and result2 == 3 and result3 == 3 and result4 == 3:
        print("✅ 所有测试通过！OCR记忆功能正常工作")
        print("✅ 成功识别后更新记忆")
        print("✅ 识别失败后延用上次结果")
    else:
        print("❌ 测试失败！")
        print(f"   期望: 5, 3, 3, 3")
        print(f"   实际: {result1}, {result2}, {result3}, {result4}")
        
        # 分析失败原因
        print("\n=== 失败分析 ===")
        if result3 != 3:
            print(f"   第4步期望延用3，但得到{result3}")
            if result3 == 2:
                print("   可能原因：OCR识别失败，但last_recognized_number为None")
            else:
                print(f"   可能原因：OCR意外识别出{result3}")
        if result4 != 3:
            print(f"   第5步期望延用3，但得到{result4}")
            if result4 == 2:
                print("   可能原因：OCR识别失败，但last_recognized_number为None")
            else:
                print(f"   可能原因：OCR意外识别出{result4}")

if __name__ == "__main__":
    test_simple_memory()
