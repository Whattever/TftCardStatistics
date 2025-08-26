#!/usr/bin/env python3
"""
OCR调试脚本
"""

import sys
import os
import numpy as np
import cv2

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ocr_module import NumberOCR

def debug_ocr_process():
    """调试OCR识别过程"""
    print("=== OCR调试 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    print("1. 测试数字5图像")
    # 创建一个清晰的数字5图像
    img5 = np.zeros((100, 60), dtype=np.uint8)
    cv2.putText(img5, "5", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, 255, 3)
    
    # 保存图像用于检查
    cv2.imwrite("debug_img5.png", img5)
    print(f"   图像尺寸: {img5.shape}")
    print(f"   图像已保存为: debug_img5.png")
    
    # 测试识别
    result = ocr.recognize_number(img5)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n2. 测试数字3图像")
    # 创建一个清晰的数字3图像
    img3 = np.zeros((100, 60), dtype=np.uint8)
    cv2.putText(img3, "3", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, 255, 3)
    
    # 保存图像用于检查
    cv2.imwrite("debug_img3.png", img3)
    print(f"   图像尺寸: {img3.shape}")
    print(f"   图像已保存为: debug_img3.png")
    
    # 测试识别
    result = ocr.recognize_number(img3)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n3. 测试噪点图像")
    # 创建噪点图像
    noise_img = np.random.randint(0, 30, (100, 60), dtype=np.uint8)
    cv2.imwrite("debug_noise.png", noise_img)
    print(f"   图像已保存为: debug_noise.png")
    
    # 测试识别
    result = ocr.recognize_number(noise_img)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")
    
    print("\n4. 测试纯黑图像")
    # 创建纯黑图像
    black_img = np.zeros((100, 60), dtype=np.uint8)
    cv2.imwrite("debug_black.png", black_img)
    print(f"   图像已保存为: debug_black.png")
    
    # 测试识别
    result = ocr.recognize_number(black_img)
    print(f"   识别结果: {result}")
    print(f"   当前记忆值: {ocr.last_recognized_number}")

if __name__ == "__main__":
    debug_ocr_process()
