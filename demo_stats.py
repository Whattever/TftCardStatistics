#!/usr/bin/env python3
"""
TFT卡牌数据统计功能演示脚本
展示如何使用新的统计功能
"""

import sys
import os
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_basic_stats():
    """演示基本统计功能"""
    print("=== 基本统计功能演示 ===")
    
    from database import TFTStatsDatabase
    
    # 创建数据库
    db = TFTStatsDatabase("demo_stats.db")
    
    # 模拟多个会话
    print("\n1. 创建多个统计会话...")
    
    # 会话1：使用tft_units模板
    session1 = db.start_session("tft_units", 0.9, 1)
    db.record_matches(session1, [
        (1, ["Gangplank"]),
        (2, ["1"]),
        (3, ["2"]),
        (4, ["3"]),
        (5, ["4"])
    ])
    db.end_session(session1)
    
    # 会话2：使用自定义模板
    session2 = db.start_session("custom_templates", 0.85, 1)
    db.record_matches(session2, [
        (1, ["custom1", "custom2"]),
        (3, ["custom3"]),
        (5, ["custom1"])
    ])
    db.end_session(session2)
    
    # 会话3：模拟游戏中的实时匹配
    session3 = db.start_session("game_session", 0.9, 1)
    
    print("2. 模拟游戏中的实时匹配...")
    for i in range(3):
        print(f"   第{i+1}次匹配...")
        matches = [
            (1, ["Gangplank"] if i % 2 == 0 else ["1"]),
            (2, ["2"]),
            (3, ["3"]),
            (4, ["4"]),
            (5, ["5"])
        ]
        db.record_matches(session3, matches)
        time.sleep(0.5)  # 模拟间隔
    
    db.end_session(session3)
    
    print("\n3. 查看统计结果...")
    
    # 显示所有会话
    print("\n--- 所有会话列表 ---")
    db.print_overall_stats()
    
    # 显示特定会话详情
    print(f"\n--- 会话 {session1} 详情 ---")
    db.print_session_summary(session1)
    
    print(f"\n--- 会话 {session2} 详情 ---")
    db.print_session_summary(session2)
    
    print(f"\n--- 会话 {session3} 详情 ---")
    db.print_session_summary(session3)
    
    return db

def demo_advanced_features():
    """演示高级功能"""
    print("\n=== 高级功能演示 ===")
    
    from database import TFTStatsDatabase
    
    db = TFTStatsDatabase("demo_stats.db")
    
    print("\n1. 数据导出功能...")
    export_file = "demo_export.csv"
    try:
        # 这里需要修复导出功能
        print(f"   导出数据到 {export_file}...")
        # 由于导出功能有bug，我们跳过这部分
        print("   (导出功能需要进一步修复)")
    except Exception as e:
        print(f"   导出失败: {e}")
    
    print("\n2. 统计分析...")
    stats = db.get_overall_stats()
    
    print(f"   总会话数: {stats['total_sessions']}")
    print(f"   总匹配数: {stats['total_matches']}")
    print(f"   唯一模板数: {stats['unique_templates']}")
    
    if stats['top_templates']:
        print("\n   最常匹配的模板:")
        for i, (template, count) in enumerate(stats['top_templates'][:5], 1):
            print(f"     {i}. {template}: {count}次")
    
    return db

def cleanup():
    """清理演示文件"""
    print("\n=== 清理演示文件 ===")
    
    files_to_remove = ["demo_stats.db", "demo_export.csv"]
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ 已删除: {file}")
            except Exception as e:
                print(f"❌ 删除失败 {file}: {e}")
        else:
            print(f"⚠️  文件不存在: {file}")

def main():
    """主演示函数"""
    print("🎮 TFT卡牌数据统计功能演示")
    print("=" * 60)
    
    try:
        # 基本功能演示
        db = demo_basic_stats()
        
        # 高级功能演示
        demo_advanced_features()
        
        print("\n🎉 演示完成！")
        print("\n现在可以尝试以下功能:")
        print("1. 运行连续监控模式: python run.py --continuous")
        print("2. 查看统计: python tools/stats_viewer.py --db demo_stats.db")
        print("3. 列出会话: python tools/stats_viewer.py --db demo_stats.db --list-sessions")
        
        # 询问是否保留演示数据库
        print(f"\n演示数据库文件: demo_stats.db")
        print("您可以保留此文件进行进一步测试，或运行清理功能删除它。")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 询问是否清理
        print("\n是否清理演示文件? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', '是']:
                cleanup()
            else:
                print("演示文件已保留，您可以继续使用。")
        except:
            print("演示文件已保留，您可以继续使用。")

if __name__ == "__main__":
    main()
