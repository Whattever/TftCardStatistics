#!/usr/bin/env python3
"""
数据库模块 - 用于记录TFT卡牌模板匹配的统计信息
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any
import threading

class TFTStatsDatabase:
    """TFT卡牌统计数据数据库"""
    
    def __init__(self, db_path: str = "tft_stats.db"):
        """初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.lock = threading.Lock()  # 线程安全锁
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建会话表 - 记录每次运行程序的信息
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    templates_dir TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    monitor_index INTEGER NOT NULL,
                    total_captures INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'running'
                )
            ''')
            
            # 创建匹配记录表 - 记录每次匹配的详细信息
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    capture_time TIMESTAMP NOT NULL,
                    capture_sequence INTEGER NOT NULL,  -- 当前session下的截图匹配次数
                    region_number INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    unit_name TEXT NOT NULL,  -- 单位名称（不含费用和扩展名）
                    cost INTEGER NOT NULL,    -- 费用
                    match_score REAL NOT NULL,
                    match_bbox TEXT,  -- JSON格式的边界框信息
                    level INTEGER,  -- 当前等级
                    ocr_confidence REAL,  -- OCR识别置信度
                    stage INTEGER,  -- 当前阶段号
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # 创建模板统计表 - 记录每个模板的总体统计
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS template_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL,  -- 移除UNIQUE约束
                    unit_name TEXT NOT NULL,  -- 单位名称（不含费用和扩展名）
                    cost INTEGER NOT NULL,    -- 费用
                    level INTEGER,      -- 当前等级
                    total_matches INTEGER DEFAULT 0,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    avg_score REAL DEFAULT 0.0,
                    region_distribution TEXT  -- JSON格式的区域分布统计
                )
            ''')
            
            # 创建复合索引，确保unit_name + cost + level
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unit_cost_ocr 
                ON template_stats (unit_name, cost, level)
            ''')
            
            conn.commit()
            conn.close()
    
    def clear_all_data(self):
        """清除所有表的数据但保留表结构"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # 清除所有表的数据
                cursor.execute('DELETE FROM matches')
                cursor.execute('DELETE FROM template_stats')
                cursor.execute('DELETE FROM sessions')
                
                # 重置自增ID
                cursor.execute('DELETE FROM sqlite_sequence WHERE name IN (?, ?, ?)', 
                            ('matches', 'template_stats', 'sessions'))
                
                conn.commit()
                print("✅ 数据库数据已清除，表结构保留")
                
            except Exception as e:
                print(f"❌ 清除数据失败: {e}")
                conn.rollback()
            finally:
                conn.close()

    def start_session(self, templates_dir: str, threshold: float, monitor_index: int) -> int:
        """开始一个新的统计会话
        
        Args:
            templates_dir: 模板目录
            threshold: 匹配阈值
            monitor_index: 显示器索引
            
        Returns:
            会话ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (start_time, templates_dir, threshold, monitor_index)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now(), templates_dir, threshold, monitor_index))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"📊 Started new statistics session (ID: {session_id})")
            return session_id
    
    def end_session(self, session_id: int):
        """结束统计会话
        
        Args:
            session_id: 会话ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET end_time = ?, status = 'completed'
                WHERE id = ?
            ''', (datetime.now(), session_id))
            
            conn.commit()
            conn.close()
            
            print(f"📊 Statistics session {session_id} ended")
    
    def record_matches(self, session_id: int, matches: List[Tuple[int, List[str]]], 
                       match_details: List[Dict[str, Any]] = None, stage: int = None):
        """记录匹配结果
        
        Args:
            session_id: 会话ID
            matches: 匹配结果列表，格式为 [(区域号, [模板名列表]), ...]
            match_details: 详细的匹配信息，包含分数、边界框和OCR结果等
        """
        if not matches:
            return
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 更新会话的截图次数
            cursor.execute('''
                UPDATE sessions 
                SET total_captures = total_captures + 1
                WHERE id = ?
            ''', (session_id,))
            
            # 获取当前会话的截图次数，用于设置capture_sequence
            cursor.execute('''
                SELECT total_captures FROM sessions WHERE id = ?
            ''', (session_id,))
            current_capture_count = cursor.fetchone()[0]
            
            # 记录每次匹配
            for i, (region_num, template_names) in enumerate(matches):
                for template_name in template_names:
                    # 解析模板名称，提取费用和单位名称
                    unit_name, cost = self._parse_template_name(template_name)
                    
                    # 获取匹配详情
                    score = 1.0  # 默认分数
                    bbox = "{}"  # 默认边界框
                    level_number = None  # 默认OCR结果
                    ocr_confidence = None  # 默认OCR置信度
                    
                    if match_details and i < len(match_details):
                        detail = match_details[i]
                        if 'score' in detail:
                            score = detail['score']
                        if 'bbox' in detail:
                            bbox = json.dumps(detail['bbox'])
                        if 'level' in detail:
                            level_number = detail['level']
                        if 'ocr_confidence' in detail:
                            ocr_confidence = detail['ocr_confidence']
                    
                    cursor.execute('''
                        INSERT INTO matches (session_id, capture_time, capture_sequence, region_number, 
                                          template_name, unit_name, cost, match_score, match_bbox, level, ocr_confidence, stage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (session_id, datetime.now(), current_capture_count, region_num, template_name, unit_name, cost, score, bbox, level_number, ocr_confidence, stage))
                    
                    # 更新模板统计
                    self._update_template_stats(cursor, template_name, unit_name, cost, region_num, score, level_number)
            
            conn.commit()
            conn.close()
            
            print(f"📊 Recorded {len(matches)} region match results with OCR data")
    
    def _parse_template_name(self, template_name: str) -> Tuple[str, int]:
        """解析模板名称，提取单位名称和费用
        
        Args:
            template_name: 模板文件名，格式为 "Xc_Y.png"
            
        Returns:
            (unit_name, cost): 单位名称和费用
        """
        try:
            # 移除.png扩展名
            name_without_ext = template_name.replace('.png', '').replace('.PNG', '')
            
            # 查找第一个下划线的位置
            underscore_pos = name_without_ext.find('_')
            if underscore_pos == -1:
                # 如果没有下划线，返回原名称和默认费用0
                return name_without_ext, 0
            
            # 提取费用部分（下划线前的部分）
            cost_part = name_without_ext[:underscore_pos]
            
            # 检查费用部分是否以数字开头，以'c'结尾
            if cost_part.endswith('c') and cost_part[:-1].isdigit():
                cost = int(cost_part[:-1])
                unit_name = name_without_ext[underscore_pos + 1:]
                return unit_name, cost
            else:
                # 如果格式不正确，返回原名称和默认费用0
                return name_without_ext, 0
                
        except Exception as e:
            print(f"⚠️ 解析模板名称 '{template_name}' 时出错: {e}")
            return template_name, 0
    
    def _update_template_stats(self, cursor, template_name: str, unit_name: str, cost: int, region_num: int, score: float, level_number: int = None):
        """更新模板统计信息"""
        # 根据unit_name、cost和level_number的组合来查找记录
        if level_number is not None:
            cursor.execute('''
                SELECT * FROM template_stats 
                WHERE unit_name = ? AND cost = ? AND level = ?
            ''', (unit_name, cost, level_number))
        else:
            # 如果没有OCR数字，仍然使用template_name查找（向后兼容）
            cursor.execute('SELECT * FROM template_stats WHERE template_name = ?', (template_name,))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            if level_number is not None:
                cursor.execute('''
                    UPDATE template_stats 
                    SET total_matches = total_matches + 1,
                        last_seen = ?,
                        avg_score = (avg_score * total_matches + ?) / (total_matches + 1)
                    WHERE unit_name = ? AND cost = ? AND level = ?
                ''', (datetime.now(), score, unit_name, cost, level_number))
            else:
                cursor.execute('''
                    UPDATE template_stats 
                    SET total_matches = total_matches + 1,
                        last_seen = ?,
                        avg_score = (avg_score * total_matches + ?) / (total_matches + 1)
                    WHERE template_name = ?
                ''', (datetime.now(), score, template_name))
            
            # 更新区域分布
            if level_number is not None:
                cursor.execute('''
                    SELECT region_distribution FROM template_stats 
                    WHERE unit_name = ? AND cost = ? AND level = ?
                ''', (unit_name, cost, level_number))
            else:
                cursor.execute('SELECT region_distribution FROM template_stats WHERE template_name = ?', (template_name,))
            
            region_dist = cursor.fetchone()[0]
            if region_dist:
                dist = json.loads(region_dist)
            else:
                dist = {}
            
            dist[str(region_num)] = dist.get(str(region_num), 0) + 1
            
            if level_number is not None:
                cursor.execute('''
                    UPDATE template_stats 
                    SET region_distribution = ?
                    WHERE unit_name = ? AND cost = ? AND level = ?
                ''', (json.dumps(dist), unit_name, cost, level_number))
            else:
                cursor.execute('''
                    UPDATE template_stats 
                    SET region_distribution = ?
                    WHERE template_name = ?
                ''', (json.dumps(dist), template_name))
        else:
            # 创建新记录
            region_dist = {str(region_num): 1}
            cursor.execute('''
                INSERT INTO template_stats (template_name, unit_name, cost, level, total_matches, first_seen, 
                                         last_seen, avg_score, region_distribution)
                VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
            ''', (template_name, unit_name, cost, level_number, datetime.now(), datetime.now(), score, json.dumps(region_dist)))
    
    def get_session_summary(self, session_id: int) -> Dict[str, Any]:
        """获取会话统计摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话统计信息字典
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取会话基本信息
            cursor.execute('''
                SELECT start_time, end_time, templates_dir, threshold, 
                       monitor_index, total_captures, status
                FROM sessions WHERE id = ?
            ''', (session_id,))
            
            session_info = cursor.fetchone()
            if not session_info:
                conn.close()
                return {}
            
            # 获取匹配统计
            cursor.execute('''
                SELECT COUNT(*) as total_matches,
                       COUNT(DISTINCT template_name) as unique_templates,
                       COUNT(DISTINCT region_number) as regions_matched,
                       COUNT(DISTINCT capture_sequence) as total_captures
                FROM matches WHERE session_id = ?
            ''', (session_id,))
            
            match_stats = cursor.fetchone()
            
            # 获取区域分布
            cursor.execute('''
                SELECT region_number, COUNT(*) as count
                FROM matches 
                WHERE session_id = ?
                GROUP BY region_number
                ORDER BY region_number
            ''', (session_id,))
            
            region_stats = dict(cursor.fetchall())
            
            # 获取模板分布
            cursor.execute('''
                SELECT template_name, unit_name, cost, COUNT(*) as count
                FROM matches 
                WHERE session_id = ?
                GROUP BY template_name, unit_name, cost
                ORDER BY count DESC
            ''', (session_id,))
            
            template_stats = []
            for row in cursor.fetchall():
                template_stats.append({
                    'template_name': row[0],
                    'unit_name': row[1],
                    'cost': row[2],
                    'count': row[3]
                })
            
            # 获取截图序列分布
            cursor.execute('''
                SELECT capture_sequence, COUNT(*) as count
                FROM matches 
                WHERE session_id = ?
                GROUP BY capture_sequence
                ORDER BY capture_sequence
            ''', (session_id,))
            
            capture_sequence_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'session_id': session_id,
                'start_time': session_info[0],
                'end_time': session_info[1],
                'templates_dir': session_info[2],
                'threshold': session_info[3],
                'monitor_index': session_info[4],
                'total_captures': session_info[5],
                'status': session_info[6],
                'total_matches': match_stats[0] if match_stats else 0,
                'unique_templates': match_stats[1] if match_stats else 0,
                'regions_matched': match_stats[2] if match_stats else 0,
                'total_captures_from_matches': match_stats[3] if match_stats else 0,
                'region_distribution': region_stats,
                'template_distribution': template_stats,
                'capture_sequence_distribution': capture_sequence_stats
            }
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """获取总体统计信息
        
        Returns:
            总体统计信息字典
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总会话数
            cursor.execute('SELECT COUNT(*) FROM sessions')
            total_sessions = cursor.fetchone()[0]
            
            # 总匹配数
            cursor.execute('SELECT COUNT(*) FROM matches')
            total_matches = cursor.fetchone()[0]
            
            # 唯一模板数
            cursor.execute('SELECT COUNT(*) FROM template_stats')
            unique_templates = cursor.fetchone()[0]
            
            # 最常匹配的模板
            cursor.execute('''
                SELECT template_name, unit_name, cost, total_matches
                FROM template_stats
                ORDER BY total_matches DESC
                LIMIT 10
            ''')
            top_templates = cursor.fetchall()
            
            # 最近的活动
            cursor.execute('''
                SELECT template_name, unit_name, cost, last_seen, total_matches
                FROM template_stats
                ORDER BY last_seen DESC
                LIMIT 5
            ''')
            recent_activity = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_sessions': total_sessions,
                'total_matches': total_matches,
                'unique_templates': unique_templates,
                'top_templates': top_templates,
                'recent_activity': recent_activity
            }
    
    def print_session_summary(self, session_id: int):
        """Print session statistics summary"""
        summary = self.get_session_summary(session_id)
        if not summary:
            print("❌ Session information not found")
            return
        
        print(f"\n📊 Session {session_id} Statistics Summary")
        print("=" * 50)
        print(f"Start Time: {summary['start_time']}")
        if summary['end_time']:
            print(f"End Time: {summary['end_time']}")
        print(f"Templates Directory: {summary['templates_dir']}")
        print(f"Match Threshold: {summary['threshold']}")
        print(f"Monitor Index: {summary['monitor_index']}")
        print(f"Total Captures: {summary['total_captures']}")
        print(f"Status: {summary['status']}")
        print(f"Total Matches: {summary['total_matches']}")
        print(f"Unique Templates: {summary['unique_templates']}")
        print(f"Regions Matched: {summary['regions_matched']}")
        print(f"Total Captures from Matches: {summary['total_captures_from_matches']}")
        
        if summary['region_distribution']:
            print("\nRegion Distribution:")
            for region, count in summary['region_distribution'].items():
                print(f"  Region {region}: {count} times")
        
        if summary['template_distribution']:
            print("\nTemplate Distribution:")
            for template_info in summary['template_distribution']:
                template_name = template_info['template_name']
                unit_name = template_info['unit_name']
                cost = template_info['cost']
                count = template_info['count']
                print(f"  {template_info['template_name']} (费用{cost}: {unit_name}): {count} times")
        
        if summary['capture_sequence_distribution']:
            print("\nCapture Sequence Distribution:")
            for sequence, count in summary['capture_sequence_distribution'].items():
                print(f"  Capture #{sequence}: {count} matches")
    
    def print_overall_stats(self):
        """Print overall statistics information"""
        stats = self.get_overall_stats()
        
        print(f"\n📊 Overall Statistics")
        print("=" * 50)
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Total Matches: {stats['total_matches']}")
        print(f"Unique Templates: {stats['unique_templates']}")
        
        if stats['top_templates']:
            print("\nMost Frequently Matched Templates:")
            for i, (template, unit_name, cost, count) in enumerate(stats['top_templates'], 1):
                print(f"  {i}. {template} (费用{cost}: {unit_name}): {count} times")
        
        if stats['recent_activity']:
            print("\nRecent Activity:")
            for template, unit_name, cost, last_seen, total_matches in stats['recent_activity']:
                print(f"  {template} (费用{cost}: {unit_name}): Last matched {last_seen}, Total {total_matches} times")
    
    def get_latest_capture_sequence(self) -> int:
        """获取数据库中最新的capture_sequence值
        
        Returns:
            int: 最新的capture_sequence值，如果没有记录则返回0
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 查询最新的capture_sequence值
                cursor.execute('''
                    SELECT MAX(capture_sequence) FROM matches
                ''')
                
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0] is not None:
                    return result[0]
                else:
                    return 0
                    
        except Exception as e:
            print(f"⚠️ 获取最新capture_sequence时出错: {e}")
            return 0

    def _get_connection(self):
        """获取数据库连接（内部使用）"""
        return sqlite3.connect(self.db_path)
