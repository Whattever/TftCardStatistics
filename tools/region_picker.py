#!/usr/bin/env python3
"""
区域选择器工具
用于可视化选择屏幕截取区域，返回精确的坐标参数
"""

import cv2
import numpy as np
from mss import mss
from typing import Tuple, Optional
import argparse


class RegionPicker:
    """屏幕区域选择器，用于可视化选择截取区域"""
    
    def __init__(self, monitor_index: int = 1):
        self.monitor_index = monitor_index
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.image = None
        self.window_name = "Region Picker - Click and drag to select region"
        
    def mouse_callback(self, event, x, y, flags, param):
        """鼠标事件回调函数"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)
    
    def capture_screen(self) -> np.ndarray:
        """截取当前屏幕"""
        with mss() as sct:
            monitor = sct.monitors[self.monitor_index]
            img = sct.grab(monitor)
            arr = np.asarray(img, dtype=np.uint8)
            return arr[:, :, :3]  # 转换为BGR格式
    
    def draw_selection(self, img: np.ndarray) -> np.ndarray:
        """在图像上绘制选择框"""
        display_img = img.copy()
        
        if self.start_point and self.end_point:
            # 绘制选择框
            cv2.rectangle(display_img, self.start_point, self.end_point, (0, 255, 0), 2)
            
            # 计算区域信息
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)
            
            # 显示区域信息
            info_text = f"Region: x={x}, y={y}, w={w}, h={h}"
            cv2.putText(display_img, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示当前鼠标位置
            if self.end_point:
                cv2.putText(display_img, f"Mouse: {self.end_point}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 显示命令行参数格式
            cmd_text = f"Command: --region {x},{y},{w},{h}"
            cv2.putText(display_img, cmd_text, (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return display_img
    
    def pick_region(self) -> Optional[Tuple[int, int, int, int]]:
        """启动区域选择器，返回选择的区域坐标 (x, y, w, h)"""
        # 截取屏幕
        self.image = self.capture_screen()
        
        # 创建窗口并设置鼠标回调
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("=== 区域选择器 ===")
        print("使用说明:")
        print("1. 点击并拖拽鼠标选择区域")
        print("2. 按 'r' 重新选择")
        print("3. 按 'Enter' 确认选择")
        print("4. 按 'Esc' 取消")
        print("5. 按 'h' 显示帮助")
        
        while True:
            # 绘制选择框
            display_img = self.draw_selection(self.image)
            cv2.imshow(self.window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == 13:  # Enter
                if self.start_point and self.end_point:
                    # 计算最终坐标
                    x1, y1 = self.start_point
                    x2, y2 = self.end_point
                    x, y = min(x1, x2), min(y1, y2)
                    w, h = abs(x2 - x1), abs(y2 - y1)
                    
                    cv2.destroyAllWindows()
                    return (x, y, w, h)
            elif key == ord('r'):  # 重新选择
                self.start_point = None
                self.end_point = None
            elif key == ord('h'):  # 显示帮助
                self.show_help()
        
        cv2.destroyAllWindows()
        return None
    
    def show_help(self):
        """显示帮助信息"""
        print("\n=== 帮助信息 ===")
        print("快捷键:")
        print("  ESC   - 取消选择并退出")
        print("  Enter - 确认当前选择")
        print("  r     - 重新选择区域")
        print("  h     - 显示此帮助信息")
        print("\n使用方法:")
        print("1. 点击并拖拽鼠标选择矩形区域")
        print("2. 调整选择框大小和位置")
        print("3. 按 Enter 确认选择")
        print("4. 程序会输出命令行参数格式")
        print("\n输出格式:")
        print("--region x,y,宽度,高度")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="屏幕区域选择器")
    parser.add_argument("--monitor", type=int, default=1, help="显示器索引 (默认: 1)")
    parser.add_argument("--show-help", action="store_true", help="显示详细帮助信息")
    
    args = parser.parse_args()
    
    if args.show_help:
        print("=== 区域选择器使用说明 ===")
        print("用途: 可视化选择屏幕截取区域，返回精确的坐标参数")
        print("\n命令行参数:")
        print("  --monitor N    指定显示器索引 (默认: 1)")
        print("  --help, -h    显示此帮助信息")
        print("\n使用步骤:")
        print("1. 运行程序: python tools/region_picker.py")
        print("2. 点击并拖拽鼠标选择区域")
        print("3. 按 Enter 确认选择")
        print("4. 复制输出的命令行参数")
        print("5. 在主程序中使用该参数")
        return
    
    try:
        picker = RegionPicker(monitor_index=args.monitor)
        result = picker.pick_region()
        
        if result:
            x, y, w, h = result
            print(f"\n=== 选择的区域 ===")
            print(f"坐标: x={x}, y={y}, w={w}, h={h}")
            print(f"命令行参数: --region {x},{y},{w},{h}")
            print(f"\n使用方法:")
            print(f"python -m src.main --templates_dir tft_units --region {x},{y},{w},{h} --show")
        else:
            print("未选择任何区域")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")


if __name__ == "__main__":
    main()
