# TFT卡牌数据统计功能指南

## 概述

数据统计功能是TFT卡牌统计工具的新增功能，它能够自动记录每次模板匹配的结果，包括匹配次数、匹配分数、区域分布等详细信息。这些数据可以帮助用户分析游戏中的卡牌出现频率和分布模式。

## 功能特性

### 📊 自动数据记录
- **会话管理**: 每次运行程序时自动创建新的统计会话
- **实时记录**: 每次D触发匹配时自动记录结果
- **详细信息**: 记录匹配分数、边界框、时间戳等完整信息

### 📈 统计分析
- **会话统计**: 单次运行的详细统计信息
- **总体统计**: 所有历史数据的汇总分析
- **模板分析**: 每个模板的匹配频率和区域分布
- **趋势分析**: 基于时间的数据趋势

### 💾 数据持久化
- **SQLite数据库**: 使用轻量级数据库存储所有数据
- **自动备份**: 数据自动保存，程序重启后数据不丢失
- **数据导出**: 支持导出为CSV格式进行进一步分析

## 使用方法

### 1. 启用统计功能

#### 连续监控模式（推荐）
```bash
# 启动连续监控模式，自动启用统计功能
python run.py --continuous

# 自定义参数
python run.py --continuous --templates_dir my_templates --threshold 0.7
```

#### 单次运行模式
```bash
# 启用统计功能
python run.py --templates_dir tft_units --use-fixed-regions --enable-stats

# 单模板匹配
python run.py --template tft_units/example.png --use-fixed-regions --enable-stats
```

### 2. 查看统计数据

#### 基本统计查看
```bash
# 查看总体统计
python tools/stats_viewer.py

# 查看特定会话统计
python tools/stats_viewer.py --session 1

# 列出所有会话
python tools/stats_viewer.py --list-sessions
```

#### 数据导出
```bash
# 导出为CSV文件（使用英文标题，避免乱码）
python tools/stats_viewer.py --export my_stats.csv

# 导出特定会话数据
python tools/stats_viewer.py --session 1 --export session_1.csv
```

#### Windows用户
```bash
# 使用批处理文件
tools/view_stats.bat

# 带参数运行
tools/view_stats.bat --overall
tools/view_stats.bat --list-sessions
```

## 数据库结构

### 会话表 (sessions)
记录每次程序运行的基本信息：
- `id`: 会话唯一标识
- `start_time`: 开始时间
- `end_time`: 结束时间
- `templates_dir`: 使用的模板目录
- `threshold`: 匹配阈值
- `monitor_index`: 显示器索引
- `total_captures`: 总截图次数
- `status`: 会话状态

### 匹配记录表 (matches)
记录每次匹配的详细信息：
- `id`: 记录唯一标识
- `session_id`: 关联的会话ID
- `capture_time`: 截图时间
- `region_number`: 区域编号
- `template_name`: 匹配的模板名称
- `match_score`: 匹配分数
- `match_bbox`: 匹配边界框（JSON格式）

### 模板统计表 (template_stats)
记录每个模板的总体统计：
- `id`: 记录唯一标识
- `template_name`: 模板名称
- `total_matches`: 总匹配次数
- `first_seen`: 首次出现时间
- `last_seen`: 最后出现时间
- `avg_score`: 平均匹配分数
- `region_distribution`: 区域分布统计（JSON格式）

## 统计信息解读

### 会话统计
- **总截图次数**: 该会话中按D的次数
- **总匹配数**: 所有区域匹配成功的总次数
- **唯一模板数**: 匹配到的不同模板数量
- **匹配区域数**: 有匹配结果的区域数量
- **区域分布**: 每个区域的匹配次数
- **模板分布**: 每个模板的匹配次数

### 总体统计
- **总会话数**: 程序运行的总次数
- **总匹配数**: 所有历史匹配的总次数
- **唯一模板数**: 历史上匹配过的不同模板数量
- **最常匹配的模板**: 按匹配次数排序的前10个模板
- **最近的活动**: 最近匹配过的模板及其统计

### 数据趋势分析
通过分析不同时间段的统计数据，可以：
- 了解卡牌出现的时间规律
- 分析游戏策略的变化
- 评估模板匹配的准确性
- 优化匹配阈值设置

## 实际应用场景

### 1. 游戏数据分析
- 统计特定卡牌的出现频率
- 分析卡牌在不同区域的分布
- 评估游戏平衡性

### 2. 程序优化
- 监控匹配准确率
- 调整匹配阈值
- 优化模板图片质量

### 3. 数据导出分析
- 导出数据到Excel进行图表分析
- 生成统计报告
- 数据可视化展示

## 注意事项

### 1. 数据库文件
- 统计数据库文件 `tft_stats.db` 会自动创建在程序运行目录
- 建议定期备份数据库文件
- 数据库文件可以安全删除，重新运行程序会创建新的数据库

### 2. 性能影响
- 统计功能对程序性能影响很小
- 数据库操作使用线程安全锁，不会影响截图和匹配速度
- 大量数据时建议定期清理旧数据

### 3. 数据准确性
- 统计数据的准确性依赖于模板匹配的准确性
- 建议定期检查匹配结果，确保统计数据的可靠性
- 可以通过调整匹配阈值来提高准确性

## 故障排除

### 常见问题

#### 1. 数据库文件无法创建
- 检查程序运行目录的写入权限
- 确保磁盘空间充足
- 检查是否有其他程序占用数据库文件

#### 2. 统计数据不显示
- 确认程序已启用统计功能
- 检查是否有匹配结果
- 验证数据库文件是否存在

#### 3. 导出功能失败
- 检查目标目录的写入权限
- 确保目标文件没有被其他程序占用
- 验证文件路径的正确性

### 调试方法
```bash
# 检查数据库文件
ls -la tft_stats.db

# 查看数据库内容（需要SQLite工具）
sqlite3 tft_stats.db ".tables"
sqlite3 tft_stats.db "SELECT * FROM sessions LIMIT 5;"
```

## 总结

数据统计功能为TFT卡牌统计工具提供了强大的数据分析能力，通过自动记录和分析匹配数据，用户可以深入了解游戏中的卡牌分布模式，优化程序设置，并为游戏策略提供数据支持。无论是游戏玩家还是开发者，都能从中获得有价值的 insights。
