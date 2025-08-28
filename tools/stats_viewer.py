#!/usr/bin/env python3
"""
TFT卡牌统计数据查看工具
用于查看和分析模板匹配的统计信息
"""

import sys
import os
import argparse
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import TFTStatsDatabase

def main():
    parser = argparse.ArgumentParser(description="TFT卡牌统计数据查看工具")
    parser.add_argument("--db", default="tft_stats.db", help="数据库文件路径")
    parser.add_argument("--session", type=int, help="查看特定会话的统计信息")
    parser.add_argument("--overall", action="store_true", help="显示总体统计信息")
    parser.add_argument("--list-sessions", action="store_true", help="列出所有会话")
    parser.add_argument("--export", help="导出数据到CSV文件")
    parser.add_argument("--export-new", help="导出新的CSV格式（包含特定字段）到指定文件")
    
    args = parser.parse_args()
    
    # Check if database file exists
    if not os.path.exists(args.db):
        print(f"❌ Database file not found: {args.db}")
        print("Please run --continuous mode first to create database")
        return
    
    db = TFTStatsDatabase(args.db)
    
    if args.session:
        # 显示特定会话的统计
        db.print_session_summary(args.session)
    
    elif args.list_sessions:
        # 列出所有会话
        list_all_sessions(db)
    
    elif args.overall:
        # 显示总体统计
        db.print_overall_stats()
    
    elif args.export:
        # 导出数据
        export_data(db, args.export)
    
    elif args.export_new:
        # 导出新的CSV格式
        export_new_data(db, args.export_new)
    
    else:
        # Default: show overall statistics
        print("=== TFT Card Statistics Viewer ===")
        print("Use --help to see all available options")
        print()
        db.print_overall_stats()

def list_all_sessions(db):
    """List all sessions"""
    print("=== All Sessions List ===")
    
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, start_time, end_time, templates_dir, threshold, 
                   monitor_index, total_captures, status
            FROM sessions
            ORDER BY start_time DESC
        ''')
        
        sessions = cursor.fetchall()
        conn.close()
        
        if not sessions:
            print("No session records found")
            return
        
        print(f"{'ID':<4} {'Start Time':<19} {'End Time':<19} {'Status':<10} {'Captures':<6} {'Templates':<15}")
        print("-" * 90)
        
        for session in sessions:
            session_id, start_time, end_time, templates_dir, threshold, monitor_index, total_captures, status = session
            
            # Format time
            start_str = str(start_time)[:19] if start_time else "N/A"
            end_str = str(end_time)[:19] if end_time else "N/A"
            
            # Extract template directory name
            templates_short = os.path.basename(templates_dir) if templates_dir else "N/A"
            
            print(f"{session_id:<4} {start_str:<19} {end_str:<19} {status:<10} {total_captures:<6} {templates_short:<15}")
            
    except Exception as e:
        print(f"❌ Failed to list sessions: {e}")
        import traceback
        traceback.print_exc()

def export_data(db, filename):
    """Export data to CSV file"""
    print(f"Exporting data to {filename}...")
    
    conn = db._get_connection()
    cursor = conn.cursor()
    
    # Export session data
    cursor.execute('''
        SELECT id, start_time, end_time, templates_dir, threshold, 
               monitor_index, total_captures, status
        FROM sessions
        ORDER BY start_time
    ''')
    
    sessions = cursor.fetchall()
    
    # Export match data
    cursor.execute('''
        SELECT session_id, capture_time, region_number, template_name, 
               match_score, match_bbox, level, ocr_confidence
        FROM matches
        ORDER BY session_id, capture_time
    ''')
    
    matches = cursor.fetchall()
    
    # Export template statistics
    cursor.execute('''
        SELECT template_name, total_matches, first_seen, last_seen, 
               avg_score, region_distribution
        FROM template_stats
        ORDER BY total_matches DESC
    ''')
    
    template_stats = cursor.fetchall()
    
    conn.close()
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Write session data
            f.write("=== Session Data ===\n")
            f.write("ID,Start Time,End Time,Templates Directory,Threshold,Monitor Index,Total Captures,Status\n")
            for session in sessions:
                f.write(','.join(str(field) if field is not None else '' for field in session) + '\n')
            
            f.write("\n=== Match Data ===\n")
            f.write("Session ID,Capture Time,Region Number,Template Name,Match Score,Match BBox,OCR Number,OCR Confidence\n")
            for match in matches:
                f.write(','.join(str(field) if field is not None else '' for field in match) + '\n')
            
            f.write("\n=== Template Statistics ===\n")
            f.write("Template Name,Total Matches,First Seen,Last Seen,Average Score,Region Distribution\n")
            for stat in template_stats:
                f.write(','.join(str(field) if field is not None else '' for field in stat) + '\n')
        
        print(f"✅ Data successfully exported to {filename}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

def export_new_data(db, filename):
    """导出新的CSV格式数据（包含特定字段）"""
    print(f"导出新的CSV格式数据到 {filename}...")
    
    conn = db._get_connection()
    cursor = conn.cursor()
    
    try:
        # 查询matches表的指定字段
        cursor.execute('''
            SELECT capture_sequence, unit_name, cost, level
            FROM matches
            ORDER BY capture_sequence, unit_name
        ''')
        matches_data = cursor.fetchall()
        
        # 查询template_stats表的指定字段
        cursor.execute('''
            SELECT id, unit_name, cost, level, total_matches
            FROM template_stats
            ORDER BY id
        ''')
        template_stats_data = cursor.fetchall()
        
        conn.close()
        
        # 写入CSV文件
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            import csv
            writer = csv.writer(csvfile)
            
            # 写入matches表数据
            writer.writerow(['=== MATCHES TABLE ==='])
            writer.writerow(['capture_sequence', 'unit_name', 'cost', 'level'])
            for row in matches_data:
                writer.writerow(row)
            
            # 写入空行分隔
            writer.writerow([])
            
            # 写入template_stats表数据
            writer.writerow(['=== TEMPLATE_STATS TABLE ==='])
            writer.writerow(['id', 'unit_name', 'cost', 'level', 'total_matches'])
            for row in template_stats_data:
                writer.writerow(row)
        
        print(f"✅ 新CSV格式数据已导出到: {filename}")
        print(f"  - matches表: {len(matches_data)} 条记录")
        print(f"  - template_stats表: {len(template_stats_data)} 条记录")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
