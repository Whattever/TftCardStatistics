#!/usr/bin/env python3
"""
OCR功能测试脚本
测试数字识别功能是否正常工作
"""

import sys
import os
import cv2
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ocr_module():
    """测试OCR模块基本功能"""
    print("=== 测试OCR模块基本功能 ===")
    
    try:
        from ocr_module import NumberOCR
        
        # 创建OCR实例
        ocr = NumberOCR()
        print("✅ OCR实例创建成功")
        
        # 测试图像预处理
        print("\n测试图像预处理...")
        test_img = np.zeros((30, 20), dtype=np.uint8)
        cv2.putText(test_img, "5", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)
        
        processed = ocr.preprocess_image(test_img)
        print(f"✅ 图像预处理成功，输出尺寸: {processed.shape}")
        
        # 测试数字识别
        print("\n测试数字识别...")
        result = ocr.recognize_number(test_img)
        print(f"✅ 数字识别结果: {result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入OCR模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ OCR测试失败: {e}")
        return False

def test_ocr_with_real_image():
    """测试OCR与真实图像"""
    print("\n=== 测试OCR与真实图像 ===")
    
    try:
        from ocr_module import NumberOCR
        
        # 创建OCR实例
        ocr = NumberOCR()
        
        # 创建一个模拟的数字图像
        img = np.zeros((30, 20, 3), dtype=np.uint8)
        
        # 绘制数字1-9进行测试
        for i in range(1, 10):
            test_img = img.copy()
            cv2.putText(test_img, str(i), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # 识别数字
            result = ocr.recognize_number(test_img)
            print(f"数字 {i}: 识别结果 = {result}")
            
            # 保存测试图像
            cv2.imwrite(f"test_digit_{i}.png", test_img)
        
        print("✅ 真实图像测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 真实图像测试失败: {e}")
        return False

def test_ocr_region_extraction():
    """测试OCR区域提取功能"""
    print("\n=== 测试OCR区域提取功能 ===")
    
    try:
        from ocr_module import NumberOCR
        
        # 创建OCR实例
        ocr = NumberOCR()
        
        # 创建一个大图像，在指定位置放置数字
        full_img = np.zeros((1200, 1920, 3), dtype=np.uint8)
        
        # 在OCR区域 (360, 1173, 27, 36) 放置数字
        x, y, w, h = 367, 1176, 20, 33
        cv2.putText(full_img, "7", (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 测试区域提取和识别
        result = ocr.recognize_number_from_region(full_img, (x, y, w, h))
        print(f"✅ 区域提取OCR识别结果: {result}")
        
        # 保存测试图像
        cv2.imwrite("test_full_screen.png", full_img)
        
        return True
        
    except Exception as e:
        print(f"❌ 区域提取测试失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    print("\n=== 清理测试文件 ===")
    
    files_to_remove = []
    for i in range(1, 10):
        files_to_remove.append(f"test_digit_{i}.png")
    files_to_remove.extend(["test_full_screen.png", "debug_region_original.png", "debug_region_processed.png"])
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ 已删除: {file}")
            except Exception as e:
                print(f"❌ 删除失败 {file}: {e}")

def main():
    """主测试函数"""
    print("🔍 OCR功能测试")
    print("=" * 50)
    
    # 检查依赖
    try:
        import pytesseract
        print("✅ pytesseract 已安装")
    except ImportError:
        print("❌ pytesseract 未安装，请运行: pip install pytesseract")
        print("注意: 还需要安装Tesseract OCR引擎")
        return False
    
    # 运行测试
    test1 = test_ocr_module()
    test2 = test_ocr_with_real_image()
    test3 = test_ocr_region_extraction()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"OCR模块基本功能: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"真实图像识别: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"区域提取识别: {'✅ 通过' if test3 else '❌ 失败'}")
    
    if test1 and test2 and test3:
        print("\n🎉 所有OCR测试通过！")
        print("\n现在可以在主程序中使用OCR功能:")
        print("1. 连续监控模式: python run.py --continuous")
        print("2. 单次运行: python run.py --templates_dir tft_units --use-fixed-regions --enable-stats")
    else:
        print("\n❌ 部分OCR测试失败，请检查错误信息")
    
    # 清理测试文件
    cleanup_test_files()
    
    return test1 and test2 and test3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
