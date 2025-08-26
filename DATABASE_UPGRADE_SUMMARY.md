# 数据库升级总结

## 概述
本次升级对TFT卡牌统计数据库进行了重要改进，主要包括：
1. 模板名称解析：将模板文件名解析为费用和单位名称
2. 新增capture_sequence字段：记录每个会话中的截图匹配次数

## 主要修改

### 1. 数据库表结构升级

#### matches表新增字段
- `unit_name`: 单位名称（不含费用和扩展名）
- `cost`: 费用（1-5）
- `capture_sequence`: 当前session下的截图匹配次数

#### template_stats表新增字段
- `unit_name`: 单位名称（不含费用和扩展名）
- `cost`: 费用（1-5）

### 2. 模板名称解析功能

新增`_parse_template_name`方法，能够解析TFT单位模板文件名：
- 输入格式：`Xc_Y.png`（如：`1c_Aatrox.png`）
- 输出：`(unit_name, cost)`（如：`("Aatrox", 1)`）

解析规则：
- 移除`.png`扩展名
- 查找下划线位置
- 提取费用部分（下划线前的数字+c）
- 提取单位名称（下划线后的部分）

### 3. 统计信息增强

#### 会话统计新增信息
- `total_captures_from_matches`: 从匹配记录中统计的截图次数
- `capture_sequence_distribution`: 截图序列分布统计

#### 显示格式改进
- 模板分布显示：`模板名 (费用X: 单位名): 次数`
- 新增截图序列分布显示

## 向后兼容性

- 自动检测现有数据库结构
- 自动添加缺失的字段
- 为新增字段设置合理的默认值

## 使用示例

### 模板名称解析
```python
db = TFTStatsDatabase()
unit_name, cost = db._parse_template_name("1c_Aatrox.png")
# 结果: unit_name = "Aatrox", cost = 1
```

### 统计信息显示
```
Template Distribution:
  1c_Aatrox.png (费用1: Aatrox): 5 times
  2c_Gangplank.png (费用2: Gangplank): 3 times

Capture Sequence Distribution:
  Capture #1: 3 matches
  Capture #2: 2 matches
  Capture #3: 4 matches
```

## 数据库字段说明

### matches表
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 会话ID |
| capture_time | TIMESTAMP | 截图时间 |
| capture_sequence | INTEGER | 截图序列号 |
| region_number | INTEGER | 区域编号 |
| template_name | TEXT | 模板文件名 |
| unit_name | TEXT | 单位名称 |
| cost | INTEGER | 费用 |
| match_score | REAL | 匹配分数 |
| match_bbox | TEXT | 边界框信息(JSON) |
| ocr_number | INTEGER | OCR识别数字 |
| ocr_confidence | REAL | OCR置信度 |

### template_stats表
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| template_name | TEXT | 模板文件名 |
| unit_name | TEXT | 单位名称 |
| cost | INTEGER | 费用 |
| total_matches | INTEGER | 总匹配次数 |
| first_seen | TIMESTAMP | 首次出现时间 |
| last_seen | TIMESTAMP | 最后出现时间 |
| avg_score | REAL | 平均匹配分数 |
| region_distribution | TEXT | 区域分布统计(JSON) |

## 升级后的优势

1. **数据分离**: 费用和单位名称分别存储，便于后续分析
2. **序列追踪**: 可以追踪每个会话中的截图顺序
3. **统计分析**: 支持按费用、单位名称等维度进行统计
4. **数据完整性**: 保持原有功能的同时增强数据结构
5. **向后兼容**: 现有数据不受影响，自动升级

## 注意事项

- 新字段会自动添加到现有数据库
- 模板名称解析失败时会使用默认值（费用=0，单位名=原文件名）
- 建议在升级后验证数据完整性
