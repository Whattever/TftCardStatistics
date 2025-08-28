import argparse
import os
import time
import threading
from typing import Tuple

import cv2
from pynput import keyboard

from .capture import grab_fullscreen, grab_region
from .matching import (
    match_template,
    load_templates_from_dir,
    draw_match_bbox,
)
from .database import TFTStatsDatabase
from .ocr_module import NumberOCR


# 固定的五个TFT卡牌区域
FIXED_REGIONS = [
    (645, 1240, 250, 185),   # 区域1
    (914, 1240, 250, 185),   # 区域2
    (1183, 1240, 250, 185),  # 区域3
    (1452, 1240, 250, 185),  # 区域4
    (1721, 1240, 250, 185),  # 区域5
]

# 全局变量用于控制程序运行
running = True
trigger_event = threading.Event()

def on_key_press(key):
    """键盘按键回调函数"""
    global running, trigger_event
    
    try:
        # Ctrl+F1 退出程序
        if key == keyboard.Key.f1 and keyboard.Key.ctrl in keyboard_listener.pressed_keys:
            print("\n检测到 Ctrl+F1，程序即将退出...")
            running = False
            return False
        
        # D 触发截图和匹配
        elif key == keyboard.KeyCode.from_char('d'):
            print("\n检测到 D 按键，触发截图和匹配...")
            trigger_event.set()
            
    except AttributeError:
        pass

def on_key_release(key):
    """键盘释放回调函数"""
    pass

def run_fixed_regions_matching(templates_dir="tft_units", monitor_index=1, threshold=0.85, show=False, enable_ocr=True, ocr_instance=None):
    """运行固定区域模板匹配的核心函数"""
    print("=== 执行固定区域模板匹配 ===")
    print(f"使用模板目录: {templates_dir}")
    print(f"匹配阈值: {threshold}")
    print(f"OCR识别: {'启用' if enable_ocr else '禁用'}")
    
    # 使用传入的OCR实例，如果没有则创建新的
    ocr = ocr_instance
    if enable_ocr and ocr is None:
        try:
            ocr = NumberOCR()
            print("✅ OCR识别器初始化成功")
        except Exception as e:
            print(f"⚠️ OCR识别器初始化失败: {e}")
            print("将禁用OCR功能")
            enable_ocr = False
            ocr = None  # 确保OCR为None
    
    # 定义OCR识别区域 (360, 1173, 27, 36)
    OCR_REGION = (360, 1173, 27, 36)
    
    # 对每个固定区域进行模板匹配
    all_matches = []
    match_details = []  # 存储详细的匹配信息
    
    for i, (x, y, w, h) in enumerate(FIXED_REGIONS):
        print(f"\n--- 区域{i+1} ({x},{y},{w},{h}) ---")
        region_img = grab_region((x, y, w, h), monitor_index=monitor_index)
        
        templates = load_templates_from_dir(templates_dir)
        matched_names = []
        region_detail = {}  # 存储当前区域的匹配详情
        
        for name, tmpl in templates:
            res = match_template(region_img, tmpl, threshold=threshold)
            if res is not None:
                matched_names.append(name)
                # 记录匹配详情
                if 'score' not in region_detail or res['score'] > region_detail.get('score', 0):
                    region_detail = {
                        'score': res['score'],
                        'bbox': {
                            'top_left': res['top_left'],
                            'bottom_right': res['bottom_right'],
                            'center': res['center']
                        }
                    }
                if show:
                    region_img = draw_match_bbox(region_img, res["top_left"], res["bottom_right"])
        
        if matched_names:
            print(f"区域{i+1} 匹配到的模板: {', '.join(matched_names)}")
            all_matches.append((i+1, matched_names))
            match_details.append(region_detail)
        else:
            print(f"区域{i+1} 未匹配到任何模板")
            match_details.append({})
        
        # 显示匹配结果
        if show:
            cv2.imshow(f"Region {i+1} Result", region_img)
    
    # OCR识别数字
    if enable_ocr and ocr:
        try:
            print(f"\n--- OCR识别区域 {OCR_REGION} ---")
            # 截取完整屏幕进行OCR识别
            full_screen = grab_fullscreen(monitor_index=monitor_index)
            level_number = ocr.recognize_number_from_region(full_screen, OCR_REGION)
            
            # 现在OCR总是返回一个数字（成功识别或回退值）
            print(f"✅ OCR识别结果: 数字 {level_number}")
            # 将OCR结果添加到所有匹配详情中
            for detail in match_details:
                detail['level'] = level_number
                detail['ocr_confidence'] = 0.9  # 默认置信度
                
        except Exception as e:
            print(f"❌ OCR识别出错: {e}")
            # 使用OCR模块的回退机制，而不是硬编码的默认值
            level_number = ocr._get_fallback_number()
            print(f"使用OCR回退值: {level_number}")
            for detail in match_details:
                detail['level'] = level_number
                detail['ocr_confidence'] = 0.5  # 低置信度
    
    if show and all_matches:
        print("\n按任意键关闭所有结果窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # 输出总结
    print(f"\n=== 匹配结果总结 ===")
    if all_matches:
        for region_num, templates in all_matches:
            print(f"区域{region_num}: {', '.join(templates)}")
    else:
        print("所有区域都未匹配到模板")
    
    # 显示OCR结果
    if enable_ocr and ocr:
        ocr_result = next((detail.get('level') for detail in match_details if detail.get('level')), None)
        if ocr_result is not None:
            print(f"OCR识别数字: {ocr_result}")
    
    print("\n等待下一次触发... (D: 截图匹配, Ctrl+F1: 退出)")
    return all_matches, match_details

def continuous_monitoring_mode(templates_dir="tft_units", monitor_index=1, threshold=0.68, show=False):
    """持续监控模式"""
    global running, trigger_event
    
    print("=== 持续监控模式已启动 ===")
    print("快捷键说明:")
    print("  D     - 触发截图和模板匹配")
    print("  Ctrl+F1 - 退出程序")
    print(f"模板目录: {templates_dir}")
    print(f"匹配阈值: {threshold}")
    print("程序将持续运行，等待快捷键输入...\n")
    
    # 初始化OCR实例
    try:
        ocr = NumberOCR()
        print("✅ OCR识别器初始化成功")
        enable_ocr = True
    except Exception as e:
        print(f"⚠️ OCR识别器初始化失败: {e}")
        print("将禁用OCR功能")
        enable_ocr = False
        ocr = None
    
    db = TFTStatsDatabase()
    
    session_id = db.start_session(templates_dir, threshold, monitor_index)
    
    # 启动键盘监听器
    global keyboard_listener
    keyboard_listener = keyboard.Listener(
        on_press=on_key_press,
        on_release=on_key_release
    )
    keyboard_listener.start()
    
    try:
        while running:
            # 等待触发事件或程序退出
            if trigger_event.wait(timeout=0.1):
                trigger_event.clear()
                if running:  # 确保程序仍在运行
                    # 执行匹配并记录结果
                    matches, match_details = run_fixed_regions_matching(templates_dir, monitor_index, threshold, show, enable_ocr=enable_ocr, ocr_instance=ocr)
                    
                    # 记录到数据库
                    if matches:
                        db.record_matches(session_id, matches, match_details)
                    
                    # Show current session statistics
                    print("\n" + "="*50)
                    db.print_session_summary(session_id)
                    print("="*50)
            
            time.sleep(0.01)  # 减少CPU占用
            
    except KeyboardInterrupt:
        print("\n检测到中断信号，程序退出...")
    finally:
        # End database session
        db.end_session(session_id)
        
        # Show final statistics
        print("\n" + "="*50)
        print("📊 Final Statistics Results")
        print("="*50)
        db.print_session_summary(session_id)
        print("\n" + "="*50)
        db.print_overall_stats()
        
        keyboard_listener.stop()
        cv2.destroyAllWindows()
        print("Program exited")





def main():
    parser = argparse.ArgumentParser(description="TFT Card Statistics - Fixed region capture and template match")
    parser.add_argument("--templates_dir", required=False, default="tft_units", help="Directory containing multiple templates")
    parser.add_argument("--monitor", type=int, default=1, help="Monitor index for capture (1=primary)")
    parser.add_argument("--threshold", type=float, default=0.68, help="Match threshold (0-1)")
    parser.add_argument("--show", action="store_true", help="Show visualization window")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring mode with hotkey triggers (D: capture, Ctrl+F1: exit)")
    parser.add_argument("--enable-stats", action="store_true", help="Enable statistics recording for non-continuous modes")



    args = parser.parse_args()


    
    # 持续监控模式：程序持续运行，等待快捷键触发
    if args.continuous:
        print("=== 启动持续监控模式 ===")
        continuous_monitoring_mode(
            templates_dir=args.templates_dir,
            monitor_index=args.monitor,
            threshold=args.threshold,
            show=args.show
        )
        return

    # 使用固定的5个区域进行模板匹配
    print("=== 使用固定区域模式 ===")
    print("将截取5个固定区域进行模板匹配...")
    
    if not args.templates_dir:
        raise SystemExit("请提供 --templates_dir 参数")
    
    print(f"使用模板目录: {args.templates_dir}")
    
    # 对每个固定区域进行模板匹配
    all_matches = []
    match_details = []  # 存储匹配详情，包括OCR结果
    
    # 初始化OCR识别器
    ocr = None
    try:
        ocr = NumberOCR()
        print("✅ OCR识别器初始化成功")
    except Exception as e:
        print(f"⚠️ OCR识别器初始化失败: {e}")
        print("将禁用OCR功能")
    
    # 定义OCR识别区域 (360, 1173, 27, 36)
    OCR_REGION = (360, 1173, 27, 36)
    
    for i, (x, y, w, h) in enumerate(FIXED_REGIONS):
        print(f"\n--- 区域{i+1} ({x},{y},{w},{h}) ---")
        region_img = grab_region((x, y, w, h), monitor_index=args.monitor)
        
        region_detail = {}  # 存储当前区域的匹配详情
        
        templates = load_templates_from_dir(args.templates_dir)
        matched_names = []
        for name, tmpl in templates:
            res = match_template(region_img, tmpl, threshold=args.threshold)
            if res is not None:
                matched_names.append(name)
                # 记录匹配详情
                if 'score' not in region_detail or res['score'] > region_detail.get('score', 0):
                    region_detail = {
                        'score': res['score'],
                        'bbox': {
                            'top_left': res['top_left'],
                            'bottom_right': res['bottom_right'],
                            'center': res['center']
                        }
                    }
                if args.show:
                    region_img = draw_match_bbox(region_img, res["top_left"], res["bottom_right"])
        
        if matched_names:
            print(f"区域{i+1} 匹配到的模板: {', '.join(matched_names)}")
            all_matches.append((i+1, matched_names))
            match_details.append(region_detail)
        else:
            print(f"区域{i+1} 未匹配到任何模板")
            match_details.append({})
        
        # 显示匹配结果
        if args.show:
            cv2.imshow(f"Region {i+1} Result", region_img)
        
        # OCR识别数字
        if ocr:
            try:
                print(f"\n--- OCR识别区域 {OCR_REGION} ---")
                # 截取完整屏幕进行OCR识别
                full_screen = grab_fullscreen(monitor_index=args.monitor)
                level_number = ocr.recognize_number_from_region(full_screen, OCR_REGION)
                
                # 现在OCR总是返回一个数字（成功识别或回退值）
                print(f"✅ OCR识别结果: 数字 {level_number}")
                # 将OCR结果添加到所有匹配详情中
                for detail in match_details:
                    detail['level'] = level_number
                    detail['ocr_confidence'] = 0.9  # 默认置信度
                    
            except Exception as e:
                print(f"❌ OCR识别出错: {e}")
                # 使用OCR模块的回退机制，而不是硬编码的默认值
                level_number = ocr._get_fallback_number()
                print(f"使用OCR回退值: {level_number}")
                for detail in match_details:
                    detail['level'] = level_number
                    detail['ocr_confidence'] = 0.5  # 低置信度
        
        if args.show and all_matches:
            print("\n按任意键关闭所有结果窗口...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # 输出总结
        print(f"\n=== 匹配结果总结 ===")
        if all_matches:
            for region_num, templates in all_matches:
                print(f"区域{region_num}: {', '.join(templates)}")
        else:
            print("所有区域都未匹配到模板")
        
        # 显示OCR结果
        if ocr:
            ocr_result = next((detail.get('level') for detail in match_details if detail.get('level')), None)
            if ocr_result is not None:
                print(f"OCR识别数字: {ocr_result}")
        
        # 如果启用了统计功能，记录结果到数据库
        if hasattr(args, 'enable_stats') and args.enable_stats:
            db = TFTStatsDatabase()
            session_id = db.start_session(args.templates_dir or "unknown", args.threshold, args.monitor)
            if all_matches:
                db.record_matches(session_id, all_matches, match_details)
            db.end_session(session_id)
            db.print_session_summary(session_id)
        
        return
    


if __name__ == "__main__":
    main()