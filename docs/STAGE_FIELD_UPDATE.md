# 数据库Stage字段更新说明

## 概述

为TFT卡牌统计系统的数据库`matches`表新增了`stage`字段，用于记录每次匹配时的当前阶段信息。

## 修改内容

### 1. 数据库结构更新

- **表名**: `matches`
- **新增字段**: `stage INTEGER`
- **字段说明**: 记录当前阶段号，可为NULL（对于没有阶段信息的记录）

### 2. 代码修改

#### 2.1 数据库模块 (`src/database.py`)

- 更新了`_init_database()`方法中的表创建SQL语句
- 修改了`record_matches()`方法签名，添加了`stage`参数
- 更新了INSERT语句，包含stage字段

#### 2.2 GUI启动器 (`gui_launcher.py`)

- 在`perform_matching()`方法中调用`record_matches`时传入`self.current_stage_num`
- 更新了日志信息，显示阶段信息

### 3. 数据流程

```
自动识别启动 → 阶段监控 → 阶段变化检测 → 执行匹配 → 存储到数据库
     ↓              ↓           ↓           ↓         ↓
self.stage_ocr_running → stage_ocr_monitor_loop → current_stage_num → perform_matching → record_matches(stage=current_stage_num)
```

## 使用方法

### 3.1 自动识别模式

当启用自动识别功能时：
1. 系统会自动监控阶段变化
2. 检测到阶段变化时，`self.current_stage_num`会更新
3. 执行匹配时，阶段信息会自动写入数据库

### 3.2 手动触发模式

当手动按D键触发匹配时：
1. 如果自动识别正在运行，会使用当前的`current_stage_num`
2. 如果自动识别未运行，stage字段将为NULL

## 数据库查询示例

### 查询特定阶段的匹配记录
```sql
SELECT * FROM matches WHERE stage = 3;
```

### 查询阶段分布统计
```sql
SELECT stage, COUNT(*) as count 
FROM matches 
WHERE stage IS NOT NULL 
GROUP BY stage 
ORDER BY stage;
```

### 查询特定阶段和费用的统计
```sql
SELECT unit_name, cost, COUNT(*) as count 
FROM matches 
WHERE stage = 3 AND cost = 2 
GROUP BY unit_name, cost;
```

## 兼容性说明

- **向后兼容**: 现有数据不受影响，stage字段为NULL
- **新数据**: 新记录的匹配结果会包含stage信息
- **混合数据**: 数据库中可能同时存在有stage和无stage的记录

## 注意事项

1. **阶段检测**: stage信息依赖于OCR阶段识别功能
2. **数据完整性**: 如果OCR识别失败，stage可能为NULL
3. **历史数据**: 现有的162条记录stage字段为NULL，这是正常的

## 测试验证

- ✅ 数据库迁移成功
- ✅ stage字段正确添加
- ✅ 代码修改完成
- ✅ 向后兼容性保持

## 后续建议

1. **数据分析**: 可以利用stage信息进行更详细的统计分析
2. **阶段趋势**: 分析不同阶段的卡牌出现频率
3. **策略优化**: 基于阶段信息优化游戏策略
