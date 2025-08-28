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
                # 验证数字范围（0-80）
                if 0 <= number <= 80:
                    # logger.info(f"OCR识别成功: {number}")
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
    
    # def recognize_stage_from_region(self, image, region):
    #     """专门识别stage区域的函数
    
    #     Args:
    #         image: 全屏图像
    #         region: 检测区域 (x, y, w, h)
        
    #     Returns:
    #         int: 识别出的stage值，如果识别失败返回None
    #     """
    #     try:
    #         # 截取指定区域
    #         x, y, w, h = region
    #         roi = image[y:y+h, x:x+w]
            
    #         # 转换为灰度图
    #         if len(roi.shape) == 3:
    #             roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    #         else:
    #             roi_gray = roi
            
    #         # 预处理：增强对比度
    #         roi_gray = cv2.equalizeHist(roi_gray)
            
    #         # 使用Tesseract进行OCR识别
    #         text = pytesseract.image_to_string(roi_gray, config='--psm 7 -c tessedit_char_whitelist=0123456789-')
            
    #         # 清理识别结果
    #         text = text.strip().replace(' ', '')
            
    #         # 验证格式：必须包含一个横杠"-"
    #         if '-' not in text:
    #             return None
            
    #         # 分割两个数字
    #         parts = text.split('-')
    #         if len(parts) != 2:
    #             return None
            
    #         # 提取两个数字
    #         try:
    #             num1 = int(parts[0])
    #             num2 = int(parts[1])
    #         except ValueError:
    #             return None
            
    #         # 组合成stage值（可以根据需要调整组合方式）
    #         # 方式1：直接拼接，如"1-2" -> 12
    #         stage_value = num1 * 10 + num2
            
    #         # 方式2：保持原始格式的数值表示，如"1-2" -> 102
    #         # stage_value = num1 * 100 + 2
            
    #         # 验证合理性：stage值应该在合理范围内（比如1-99）
    #         if 1 <= stage_value <= 99:
    #             return stage_value
    #         else:
    #             return None
                
    #     except Exception as e:
    #         print(f"Stage识别错误: {e}")
    #         return None
    
    # def validate_stage_increment(self, new_stage, previous_stage):
    #     """验证stage值是否合理递增
        
    #     Args:
    #         new_stage: 新识别的stage值
    #         previous_stage: 之前的stage值
            
    #     Returns:
    #         bool: 是否合理递增
    #     """
    #     if previous_stage is None:
    #         return True  # 第一次识别，总是有效
        
    #     return new_stage > previous_stage
    
    # def recognize_stage_with_validation(self, image, region, previous_stage=None):
    #     """带验证的stage识别函数
        
    #     Args:
    #         image: 全屏图像
    #         region: 检测区域
    #         previous_stage: 之前的stage值，用于验证递增性
            
    #     Returns:
    #         int: 验证通过的stage值，如果验证失败返回None
    #     """
    #     # 尝试识别stage
    #     stage_value = self.recognize_stage_from_region(image, region)
        
    #     if stage_value is None:
    #         return None
        
    #     # 验证递增性
    #     if self.validate_stage_increment(stage_value, previous_stage):
    #         return stage_value
    #     else:
    #         print(f"Stage值验证失败: {previous_stage} -> {stage_value}")
    #         return None
    
    
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

    # 图片地址
    # img_path = "C:/Users/wza19/workspace_ccstheia/TftCardStatistics/6-3.png"
    # test_img = cv2.imread(img_path)
    
    print("测试图像预处理...")
    processed = ocr.preprocess_image(test_img)
    print(f"预处理完成，图像尺寸: {processed.shape}")
    
    print("测试数字识别...")
    result = ocr.recognize_number(test_img)
    print(f"识别结果: {result}")
    
    print("OCR模块测试完成")


if __name__ == "__main__":
    test_ocr()
