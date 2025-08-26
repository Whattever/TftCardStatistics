#!/usr/bin/env python3
"""
自动截取FIXED_REGIONS区域图片并去重保存
使用方式: python tools/auto_capture.py
"""

import sys
from pathlib import Path
import time

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from capture import grab_region
from matching import match_template, load_templates_from_dir

# 固定的五个TFT卡牌区域
FIXED_REGIONS = [
    (645, 1240, 250, 185),   # 区域1
    (914, 1240, 250, 185),   # 区域2
    (1183, 1240, 250, 185),  # 区域3
    (1452, 1240, 250, 185),  # 区域4
    (1721, 1240, 250, 185),  # 区域5
]

def generate_unique_filename(base_name, save_dir, extension=".png"):
    """生成唯一的文件名，避免覆盖"""
    counter = 1
    filename = base_name + extension
    
    while (save_dir / filename).exists():
        filename = f"{base_name}_{counter:03d}{extension}"
        counter += 1
    
    return filename

def auto_capture_and_save():
    """自动截取FIXED_REGIONS区域并去重保存"""
    save_dir = Path("tft_units_test")
    save_dir.mkdir(exist_ok=True)
    
    # 加载现有模板
    existing_templates = []
    if save_dir.exists() and any(save_dir.iterdir()):
        try:
            existing_templates = load_templates_from_dir(str(save_dir))
            print(f"已加载 {len(existing_templates)} 个现有模板")
        except Exception as e:
            print(f"加载现有模板失败: {e}")
    
    # 截取并保存每个区域
    saved_count = 0
    duplicate_count = 0
    
    for i, (x, y, w, h) in enumerate(FIXED_REGIONS):
        print(f"\n--- 处理区域{i+1} ({x},{y},{w},{h}) ---")
        
        try:
            # 截取区域图片
            region_img = grab_region((x, y, w, h))
            
            # 检查是否重复
            is_dup = False
            dup_name = None
            for name, template in existing_templates:
                if match_template(region_img, template, threshold=0.95):
                    print(f"  区域{i+1} 与现有图片 {name} 重复，跳过保存")
                    is_dup = True
                    dup_name = name
                    duplicate_count += 1
                    break
            
            if not is_dup:
                # 生成唯一的文件名并保存
                timestamp = int(time.time())
                base_name = f"region_{i+1}_{x}_{y}_{w}_{h}_{timestamp}"
                filename = generate_unique_filename(base_name, save_dir)
                filepath = save_dir / filename
                
                import cv2
                cv2.imwrite(str(filepath), region_img)
                print(f"  区域{i+1} 已保存为 {filename}")
                saved_count += 1
                existing_templates.append((filename, region_img))
        
        except Exception as e:
            print(f"  区域{i+1} 处理失败: {e}")
    
    # 输出总结
    print(f"\n=== 处理完成 ===")
    print(f"新增保存: {saved_count} 张")
    print(f"重复跳过: {duplicate_count} 张")
    print(f"保存目录: {save_dir.absolute()}")

if __name__ == "__main__":
    auto_capture_and_save()
