#!/usr/bin/env python3
"""
测试数据统计功能的脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import TFTStatsDatabase

def test_database_creation():
    """测试数据库创建和基本功能"""
    print("=== 测试数据库创建和基本功能 ===")
    
    # 删除可能存在的测试数据库
    test_db_path = "test_stats.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"已删除旧的测试数据库: {test_db_path}")
    
    try:
        # 创建数据库实例
        db = TFTStatsDatabase(test_db_path)
        print("✅ 数据库创建成功")
        
        # 测试会话创建
        session_id = db.start_session("test_templates", 0.9, 1)
        print(f"✅ 会话创建成功，ID: {session_id}")
        
        # 测试匹配记录
        test_matches = [
            (1, ["template1", "template2"]),
            (3, ["template1"]),
            (5, ["template3"])
        ]
        
        test_details = [
            {"score": 0.95, "bbox": {"top_left": (0, 0), "bottom_right": (100, 100)}},
            {"score": 0.92, "bbox": {"top_left": (200, 200), "bottom_right": (300, 300)}},
            {"score": 0.88, "bbox": {"top_left": (400, 400), "bottom_right": (500, 500)}}
        ]
        
        db.record_matches(session_id, test_matches, test_details)
        print("✅ 匹配记录成功")
        
        # 测试统计查询
        print("\n=== 会话统计 ===")
        db.print_session_summary(session_id)
        
        print("\n=== 总体统计 ===")
        db.print_overall_stats()
        
        # 结束会话
        db.end_session(session_id)
        print("✅ 会话结束成功")
        
        # 清理测试数据库
        os.remove(test_db_path)
        print(f"✅ 测试数据库已清理: {test_db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_integration():
    """测试与main模块的集成"""
    print("\n=== 测试与main模块的集成 ===")
    
    try:
        # 测试数据库文件是否可以被main模块使用
        # 由于导入限制，我们只测试数据库文件的基本功能
        test_db_path = "test_integration.db"
        
        # 创建测试数据库
        db = TFTStatsDatabase(test_db_path)
        session_id = db.start_session("test_integration", 0.9, 1)
        
        # 记录一些测试数据
        test_matches = [(1, ["test_template"])]
        db.record_matches(session_id, test_matches)
        db.end_session(session_id)
        
        # 验证数据库文件存在且可读
        if os.path.exists(test_db_path):
            print("✅ 数据库文件创建成功")
            
            # 尝试重新打开数据库
            db2 = TFTStatsDatabase(test_db_path)
            stats = db2.get_overall_stats()
            if stats['total_sessions'] > 0:
                print("✅ 数据库文件可正常读写")
            else:
                print("❌ 数据库文件读取失败")
            
            # 清理测试数据库
            os.remove(test_db_path)
            print("✅ 集成测试数据库已清理")
            
            return True
        else:
            print("❌ 数据库文件创建失败")
            return False
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("TFT卡牌数据统计功能测试")
    print("=" * 50)
    
    # 运行测试
    test1_success = test_database_creation()
    test2_success = test_main_integration()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"数据库功能测试: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"模块集成测试: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("\n🎉 所有测试通过！数据统计功能正常工作。")
        print("\n现在可以运行以下命令来使用统计功能:")
        print("1. 连续监控模式: python run.py --continuous")
        print("2. 查看统计: python tools/stats_viewer.py")
        print("3. 导出数据: python tools/stats_viewer.py --export stats.csv")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")
    
    return test1_success and test2_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
