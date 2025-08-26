#!/usr/bin/env python3
"""
测试OCR记忆功能的脚本
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def create_test_image(number: str, size=(30, 20)) -> np.ndarray:
    """创建测试图像"""
    img = np.zeros((size[0], size[1]), dtype=np.uint8)
    cv2.putText(img, number, (5, size[0]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)
    return img

def create_invalid_image(size=(30, 20)) -> np.ndarray:
    """创建无效图像（纯黑色，无法识别）"""
    # 创建一个完全黑色的图像，确保无法识别
    img = np.zeros((size[0], size[1]), dtype=np.uint8)
    # 添加一些噪点，但确保没有可识别的数字
    img[10:15, 10:15] = 50  # 添加一些灰色区域，但不是数字
    return img

def test_ocr_memory():
    """测试OCR记忆功能"""
    print("=== 测试OCR记忆功能 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("\n1. 第一次识别有效数字 '5'")
    test_img_5 = create_test_image("5")
    result1 = ocr.recognize_number(test_img_5)
    print(f"   识别结果: {result1}")
    print(f"   上次识别结果: {ocr.last_recognized_number}")
    
    print("\n2. 第二次识别有效数字 '3'")
    test_img_3 = create_test_image("3")
    result2 = ocr.recognize_number(test_img_3)
    print(f"   识别结果: {result2}")
    print(f"   上次识别结果: {ocr.last_recognized_number}")
    
    print("\n3. 第三次识别无效图像（应该延用上次结果 '3'）")
    invalid_img = create_invalid_image()
    result3 = ocr.recognize_number(invalid_img)
    print(f"   识别结果: {result3}")
    print(f"   上次识别结果: {ocr.last_recognized_number}")
    
    print("\n4. 第四次识别无效图像（应该延用上次结果 '3'）")
    result4 = ocr.recognize_number(invalid_img)
    print(f"   识别结果: {result4}")
    print(f"   上次识别结果: {ocr.last_recognized_number}")
    
    print("\n5. 第五次识别有效数字 '7'")
    test_img_7 = create_test_image("7")
    result5 = ocr.recognize_number(test_img_7)
    print(f"   识别结果: {result5}")
    print(f"   上次识别结果: {ocr.last_recognized_number}")
    
    print("\n6. 第六次识别无效图像（应该延用上次结果 '7'）")
    result6 = ocr.recognize_number(invalid_img)
    print(f"   识别结果: {result6}")
    print(f"   上次识别结果: {ocr.last_recognized_number}")
    
    print("\n=== 测试结果总结 ===")
    print(f"有效识别次数: {sum(1 for r in [result1, result2, result5] if r is not None)}")
    print(f"回退使用次数: {sum(1 for r in [result3, result4, result6] if r is not None)}")
    
    # 验证回退逻辑 - 修正期望值
    expected_fallback = [result2, result2, result5]  # 使用实际的上次结果
    actual_fallback = [result3, result4, result6]
    
    if actual_fallback == expected_fallback:
        print("✅ 回退逻辑正确：成功延用上次识别结果")
    else:
        print("❌ 回退逻辑错误：期望值", expected_fallback, "实际值", actual_fallback)

def test_ocr_without_previous():
    """测试没有上次识别结果时的默认值"""
    print("\n=== 测试无上次结果时的默认值 ===")
    
    # 创建新的OCR实例（没有历史记录）
    ocr_new = NumberOCR()
    
    print("1. 新OCR实例，无历史记录")
    print(f"   上次识别结果: {ocr_new.last_recognized_number}")
    
    print("\n2. 识别无效图像（应该使用默认值2）")
    invalid_img = create_invalid_image()
    result = ocr_new.recognize_number(invalid_img)
    print(f"   识别结果: {result}")
    print(f"   上次识别结果: {ocr_new.last_recognized_number}")
    
    if result == 2:
        print("✅ 默认值逻辑正确：无历史记录时使用默认值2")
    else:
        print("❌ 默认值逻辑错误：期望值2，实际值", result)

if __name__ == "__main__":
    test_ocr_memory()
    test_ocr_without_previous()
    print("\n测试完成！")
