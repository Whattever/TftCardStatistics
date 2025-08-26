#!/usr/bin/env python3
"""
OCR记忆功能演示脚本
展示当OCR识别失败时如何自动延用上次识别结果
"""

import sys
import os
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def demo_ocr_memory():
    """演示OCR记忆功能"""
    print("=== OCR记忆功能演示 ===")
    print("这个演示展示了OCR识别失败时如何自动延用上次识别结果")
    print("如果之前没有识别结果，则使用默认值2\n")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 模拟第一次OCR识别成功")
    print("   假设识别到数字: 5")
    # 模拟成功识别
    ocr.last_recognized_number = 5
    print(f"   当前记忆的数字: {ocr.last_recognized_number}")
    
    print("\n2. 模拟第二次OCR识别失败")
    print("   识别失败，自动延用上次结果")
    fallback_result = ocr._get_fallback_number()
    print(f"   回退结果: {fallback_result}")
    
    print("\n3. 模拟第三次OCR识别成功")
    print("   假设识别到数字: 3")
    ocr.last_recognized_number = 3
    print(f"   当前记忆的数字: {ocr.last_recognized_number}")
    
    print("\n4. 模拟第四次OCR识别失败")
    print("   识别失败，自动延用上次结果")
    fallback_result = ocr._get_fallback_number()
    print(f"   回退结果: {fallback_result}")
    
    print("\n5. 模拟第五次OCR识别失败")
    print("   识别失败，自动延用上次结果")
    fallback_result = ocr._get_fallback_number()
    print(f"   回退结果: {fallback_result}")
    
    print("\n=== 演示总结 ===")
    print("✅ OCR识别成功时：更新记忆的数字")
    print("✅ OCR识别失败时：自动延用上次结果")
    print("✅ 无历史记录时：使用默认值2")
    print("✅ 确保程序不会因为OCR失败而中断")

def demo_new_ocr_instance():
    """演示新OCR实例的默认值行为"""
    print("\n=== 新OCR实例演示 ===")
    print("创建一个新的OCR实例，没有历史记录")
    
    # 创建新的OCR实例
    ocr_new = NumberOCR()
    
    print(f"新OCR实例的上次识别结果: {ocr_new.last_recognized_number}")
    
    print("\n模拟OCR识别失败（无历史记录）")
    fallback_result = ocr_new._get_fallback_number()
    print(f"回退结果: {fallback_result}")
    
    if fallback_result == 2:
        print("✅ 新实例正确使用默认值2")
    else:
        print("❌ 新实例默认值错误")

if __name__ == "__main__":
    demo_ocr_memory()
    demo_new_ocr_instance()
    
    print("\n" + "="*50)
    print("演示完成！")
    print("现在你可以在主程序中使用这个改进的OCR功能")
    print("当OCR识别失败时，程序会自动延用上次结果，确保连续性")
    print("="*50)
