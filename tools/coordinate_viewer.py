#!/usr/bin/env python3
"""
坐标查看器工具
用于实时查看屏幕像素坐标，帮助确定游戏画面截取区域
"""

import cv2
import numpy as np
from mss import mss
from typing import Tuple
import argparse


class CoordinateViewer:
    """像素坐标查看器，实时显示鼠标位置坐标"""
    
    def __init__(self, monitor_index: int = 1):
        self.monitor_index = monitor_index
        self.window_name = "Coordinate Viewer - Move mouse to see coordinates"
        
    def mouse_callback(self, event, x, y, flags, param):
        """鼠标事件回调函数，记录当前鼠标位置"""
        self.current_mouse_pos = (x, y)
    
    def capture_screen(self) -> np.ndarray:
        """截取当前屏幕"""
        with mss() as sct:
            monitor = sct.monitors[self.monitor_index]
            img = sct.grab(monitor)
            arr = np.asarray(img, dtype=np.uint8)
            return arr[:, :, :3]  # 转换为BGR格式
    
    def show_coordinates(self):
        """显示坐标查看器"""
        # 截取屏幕
        self.image = self.capture_screen()
        self.current_mouse_pos = (0, 0)
        
        # 创建窗口并设置鼠标回调
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("=== 像素坐标查看器 ===")
        print("移动鼠标查看坐标，按 'Esc' 退出")
        print("按 'c' 复制当前坐标到剪贴板")
        print("按 's' 保存当前截图")
        print("按 'h' 显示帮助信息")
        
        while True:
            # 在图像上显示坐标信息
            display_img = self.image.copy()
            
            # 显示当前鼠标位置
            x, y = self.current_mouse_pos
            cv2.putText(display_img, f"Mouse: ({x}, {y})", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # 显示屏幕分辨率
            h, w = self.image.shape[:2]
            cv2.putText(display_img, f"Screen: {w}x{h}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 显示使用提示
            cv2.putText(display_img, "Press 'c' copy coord, 's' save, 'h' help, ESC exit", (10, h-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow(self.window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == ord('c'):  # 复制坐标
                x, y = self.current_mouse_pos
                coord_text = f"{x},{y}"
                try:
                    import pyperclip
                    pyperclip.copy(coord_text)
                    print(f"坐标已复制到剪贴板: {coord_text}")
                except ImportError:
                    print(f"坐标: {coord_text} (安装 pyperclip 可自动复制到剪贴板)")
            elif key == ord('s'):  # 保存截图
                timestamp = cv2.getTickCount()
                filename = f"screenshot_{timestamp}.png"
                cv2.imwrite(filename, self.image)
                print(f"截图已保存: {filename}")
            elif key == ord('h'):  # 显示帮助
                self.show_help()
        
        cv2.destroyAllWindows()
    
    def show_help(self):
        """显示帮助信息"""
        print("\n=== 帮助信息 ===")
        print("快捷键:")
        print("  ESC - 退出程序")
        print("  c   - 复制当前鼠标坐标到剪贴板")
        print("  s   - 保存当前屏幕截图")
        print("  h   - 显示此帮助信息")
        print("\n使用方法:")
        print("1. 移动鼠标到需要记录的位置")
        print("2. 按 'c' 复制坐标")
        print("3. 记录多个关键位置的坐标")
        print("4. 计算区域参数: x,y,宽度,高度")
        print("\n示例:")
        print("左上角: (100, 200)")
        print("右下角: (500, 400)")
        print("区域参数: 100,200,400,200")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="像素坐标查看器")
    parser.add_argument("--monitor", type=int, default=1, help="显示器索引 (默认: 1)")
    parser.add_argument("--show-help", action="store_true", help="显示详细帮助信息")
    
    args = parser.parse_args()
    
    if args.show_help:
        print("=== 坐标查看器使用说明 ===")
        print("用途: 实时查看屏幕像素坐标，帮助确定游戏画面截取区域")
        print("\n命令行参数:")
        print("  --monitor N    指定显示器索引 (默认: 1)")
        print("  --help, -h    显示此帮助信息")
        print("\n使用步骤:")
        print("1. 运行程序: python tools/coordinate_viewer.py")
        print("2. 移动鼠标查看坐标")
        print("3. 按 'c' 复制坐标到剪贴板")
        print("4. 记录关键位置的坐标值")
        print("5. 按 ESC 退出")
        return
    
    try:
        viewer = CoordinateViewer(monitor_index=args.monitor)
        viewer.show_coordinates()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")


if __name__ == "__main__":
    main()
