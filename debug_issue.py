#!/usr/bin/env python3
"""
调试OCR记忆功能问题
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def debug_issue():
    """调试OCR记忆功能问题"""
    print("=== 调试OCR记忆功能问题 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 初始状态")
    print(f"   记忆值: {ocr.last_recognized_number}")
    print(f"   类型: {type(ocr.last_recognized_number)}")
    
    print("\n2. 设置记忆值为8")
    ocr.last_recognized_number = 8
    print(f"   记忆值: {ocr.last_recognized_number}")
    print(f"   类型: {type(ocr.last_recognized_number)}")
    
    print("\n3. 测试_get_fallback_number方法")
    fallback = ocr._get_fallback_number()
    print(f"   回退值: {fallback}")
    print(f"   类型: {type(fallback)}")
    
    print("\n4. 测试recognize_number方法（使用无法识别的图像）")
    # 创建一个无法识别的图像
    noise_img = np.random.randint(0, 30, (50, 30), dtype=np.uint8)
    result = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result}")
    print(f"   类型: {type(result)}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n5. 检查记忆值是否被意外修改")
    if ocr.last_recognized_number == 8:
        print("   ✅ 记忆值保持为8")
    else:
        print(f"   ❌ 记忆值被意外修改为: {ocr.last_recognized_number}")
    
    print("\n6. 再次测试回退机制")
    fallback = ocr._get_fallback_number()
    print(f"   回退值: {fallback}")
    
    print("\n7. 检查OCR模块的配置")
    print(f"   OCR配置: {ocr.config}")
    print(f"   记忆变量: {ocr.last_recognized_number}")

def test_memory_persistence():
    """测试记忆的持久性"""
    print("\n=== 测试记忆持久性 ===")
    
    ocr = NumberOCR()
    
    print("1. 设置记忆值为8")
    ocr.last_recognized_number = 8
    
    print("2. 连续调用多次识别失败")
    for i in range(5):
        noise_img = np.random.randint(0, 30, (50, 30), dtype=np.uint8)
        result = ocr.recognize_number(noise_img)
        print(f"   第{i+1}次: 结果={result}, 记忆={ocr.last_recognized_number}")
        
        if result != 8:
            print(f"   ❌ 第{i+1}次没有延用8，而是得到{result}")
            break
    else:
        print("   ✅ 连续5次都正确延用了8")

if __name__ == "__main__":
    debug_issue()
    test_memory_persistence()
    
    print("\n=== 调试总结 ===")
    print("如果问题仍然存在，可能的原因：")
    print("1. OCR模块被重新初始化")
    print("2. 记忆变量被意外清空")
    print("3. 主程序中有其他逻辑覆盖了OCR结果")
    print("4. 多线程访问导致记忆变量不一致")
