#!/usr/bin/env python3
"""
OCR安装检查脚本
检查并指导安装Tesseract OCR引擎
"""

import sys
import os
import subprocess
import platform

def check_python_dependencies():
    """检查Python依赖"""
    print("=== 检查Python依赖 ===")
    
    try:
        import pytesseract
        print("✅ pytesseract 已安装")
        return True
    except ImportError:
        print("❌ pytesseract 未安装")
        print("请运行: pip install pytesseract")
        return False

def check_tesseract_installation():
    """检查Tesseract是否已安装"""
    print("\n=== 检查Tesseract OCR引擎 ===")
    
    try:
        # 尝试导入pytesseract
        import pytesseract
        
        # 检查Tesseract是否可用
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract 已安装，版本: {version}")
            return True
        except Exception as e:
            print(f"❌ Tesseract 未正确安装或配置: {e}")
            return False
            
    except ImportError:
        print("❌ pytesseract 未安装，无法检查Tesseract")
        return False

def get_installation_instructions():
    """获取安装说明"""
    print("\n=== 安装说明 ===")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Windows 用户:")
        print("1. 下载Tesseract安装包:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. 运行安装包，选择安装路径")
        print("3. 将安装目录添加到系统PATH环境变量")
        print("4. 或者在代码中指定Tesseract路径:")
        print("   ocr = NumberOCR(tesseract_path=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')")
        
    elif system == "darwin":  # macOS
        print("macOS 用户:")
        print("使用Homebrew安装:")
        print("brew install tesseract")
        
    elif system == "linux":
        print("Linux 用户:")
        print("Ubuntu/Debian:")
        print("sudo apt-get install tesseract-ocr")
        print("\nCentOS/RHEL:")
        print("sudo yum install tesseract")
        
    print("\n安装完成后，运行以下命令验证:")
    print("python test_ocr.py")

def test_ocr_functionality():
    """测试OCR功能"""
    print("\n=== 测试OCR功能 ===")
    
    try:
        # 添加src目录到Python路径
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from ocr_module import NumberOCR
        
        # 创建OCR实例
        ocr = NumberOCR()
        print("✅ OCR模块导入成功")
        
        # 创建测试图像
        import cv2
        import numpy as np
        
        test_img = np.zeros((30, 20), dtype=np.uint8)
        cv2.putText(test_img, "5", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)
        
        # 测试识别
        result = ocr.recognize_number(test_img)
        if result == 5:
            print("✅ OCR功能测试通过")
            return True
        else:
            print(f"❌ OCR功能测试失败，期望结果: 5，实际结果: {result}")
            return False
            
    except Exception as e:
        print(f"❌ OCR功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 OCR安装检查工具")
    print("=" * 50)
    
    # 检查Python依赖
    python_ok = check_python_dependencies()
    
    # 检查Tesseract安装
    tesseract_ok = check_tesseract_installation()
    
    # 如果都正常，测试功能
    if python_ok and tesseract_ok:
        print("\n🎉 所有检查通过！")
        print("现在可以运行OCR功能了")
        
        # 测试功能
        if test_ocr_functionality():
            print("\n✅ OCR功能完全正常！")
            print("可以运行主程序:")
            print("python run.py --continuous")
        else:
            print("\n❌ OCR功能测试失败，请检查安装")
            
    else:
        print("\n❌ 需要安装或配置OCR组件")
        get_installation_instructions()
        
        if not python_ok:
            print("\n请先安装Python依赖:")
            print("pip install pytesseract")
            
        if not tesseract_ok:
            print("\n请按照上述说明安装Tesseract OCR引擎")

if __name__ == "__main__":
    main()

