#!/usr/bin/env python3
"""
OCR模块 - 用于识别指定区域的数字
"""

import cv2
import numpy as np
import pytesseract
from typing import Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NumberOCR:
    """数字OCR识别器"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """初始化OCR识别器
        
        Args:
            tesseract_path: Tesseract可执行文件路径（Windows需要）
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # 配置Tesseract参数，优化数字识别
        self.config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        
        # 记忆上次识别结果，用于OCR失败时的回退
        self.last_recognized_number = None
        
        logger.info("NumberOCR initialized")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理图像以提高OCR识别准确率
        
        Args:
            image: 输入图像
            
        Returns:
            预处理后的图像
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 调整图像大小（放大以提高识别率）
        scale_factor = 3
        h, w = gray.shape
        enlarged = cv2.resize(gray, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_CUBIC)
        
        # 应用高斯模糊去噪
        blurred = cv2.GaussianBlur(enlarged, (3, 3), 0)
        
        # 应用阈值处理，突出数字
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作，去除小噪点
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def recognize_number(self, image: np.ndarray) -> int:
        """识别图像中的数字
        
        Args:
            image: 输入图像
            
        Returns:
            识别出的数字，如果识别失败则返回上次结果或默认值2
        """
        try:
            # 预处理图像
            processed = self.preprocess_image(image)
            
            # 使用Tesseract进行OCR识别
            text = pytesseract.image_to_string(processed, config=self.config)
            
            # 清理识别结果
            text = text.strip()
            
            # 尝试提取数字
            if text and text.isdigit():
                number = int(text)
                # 验证数字范围（0-10）
                if 0 <= number <= 10:
                    logger.info(f"OCR识别成功: {number}")
                    # 更新上次识别结果
                    self.last_recognized_number = number
                    return number
                else:
                    logger.warning(f"OCR识别结果超出范围: {number}")
                    # 超出范围时使用上次结果或默认值
                    return self._get_fallback_number()
            else:
                logger.warning(f"OCR识别失败，结果: '{text}'")
                # 识别失败时使用上次结果或默认值
                return self._get_fallback_number()
                
        except Exception as e:
            logger.error(f"OCR识别出错: {e}")
            # 出错时使用上次结果或默认值
            return self._get_fallback_number()
    
    def _get_fallback_number(self) -> int:
        """获取回退数字（上次识别结果或默认值2）
        
        Returns:
            回退数字
        """
        if self.last_recognized_number is not None:
            logger.info(f"OCR识别失败，延用上次结果: {self.last_recognized_number}")
            return self.last_recognized_number
        else:
            logger.info("OCR识别失败且无上次结果，使用默认值: 2")
            return 2
    
    def recognize_number_from_region(self, full_image: np.ndarray, region: Tuple[int, int, int, int]) -> int:
        """从完整图像中截取指定区域并识别数字
        
        Args:
            full_image: 完整图像
            region: 区域坐标 (x, y, width, height)
            
        Returns:
            识别出的数字，如果识别失败则返回上次结果或默认值2
        """
        try:
            x, y, w, h = region
            
            # 截取指定区域
            region_img = full_image[y:y+h, x:x+w]
            
            if region_img.size == 0:
                logger.error(f"区域截取失败: {region}")
                return self._get_fallback_number()
            
            # 识别数字
            return self.recognize_number(region_img)
            
        except Exception as e:
            logger.error(f"区域截取和识别失败: {e}")
            return self._get_fallback_number()
    
    def debug_ocr(self, image: np.ndarray, region: Tuple[int, int, int, int], save_debug: bool = False) -> Optional[int]:
        """调试OCR识别过程，保存中间结果
        
        Args:
            image: 输入图像
            region: 区域坐标
            save_debug: 是否保存调试图像
            
        Returns:
            识别结果
        """
        x, y, w, h = region
        
        # 截取区域
        region_img = image[y:y+h, x:x+w]
        
        if save_debug:
            # 保存原始区域图像
            cv2.imwrite("debug_region_original.png", region_img)
            
            # 保存预处理后的图像
            processed = self.preprocess_image(region_img)
            cv2.imwrite("debug_region_processed.png", processed)
            
            logger.info("调试图像已保存")
        
        # 执行识别
        result = self.recognize_number(region_img)
        
        return result


def test_ocr():
    """测试OCR功能"""
    print("=== OCR模块测试 ===")
    
    # 创建OCR实例
    ocr = NumberOCR()
    
    # 测试图像预处理
    test_img = np.zeros((30, 20), dtype=np.uint8)
    cv2.putText(test_img, "5", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)
    
    print("测试图像预处理...")
    processed = ocr.preprocess_image(test_img)
    print(f"预处理完成，图像尺寸: {processed.shape}")
    
    print("测试数字识别...")
    result = ocr.recognize_number(test_img)
    print(f"识别结果: {result}")
    
    print("OCR模块测试完成")


if __name__ == "__main__":
    test_ocr()
