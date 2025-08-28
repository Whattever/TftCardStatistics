# TFT卡牌统计系统配置文件说明

## 概述

`config.json` 文件包含了TFT卡牌统计系统的所有配置参数，通过修改此文件可以自定义系统的行为，而无需修改源代码。

## 配置文件结构

### 1. 匹配设置 (`matching_settings`)

#### 基本参数
- `threshold`: 图片匹配阈值 (0.5-1.0)
- `monitor_index`: 显示器索引 (1-4)
- `enable_ocr`: 是否启用OCR功能
- `base_resolution`: 基础分辨率（不要修改）

#### 固定区域 (`fixed_regions`)
定义5个TFT卡牌检测区域，每个区域包含：
- `id`: 区域编号
- `name`: 区域名称
- `coordinates`: 坐标 [x, y, 宽度, 高度]
- `relative_coordinates`: 量化坐标 [x, y, 宽度, 高度]

#### OCR区域 (`ocr_regions`)
- `level_detection`: Level检测区域
  - `name`: 区域名称
  - `coordinates`: 坐标 [x, y, 宽度, 高度]
- `stage_detection`: Stage检测区域
  - `name`: 区域名称
  - `coordinates`: 坐标 [x, y, 宽度, 高度]

### 3. 自动识别设置 (`auto_identification`)

- `stage_monitor_interval`: 阶段监控间隔 (秒)
- `buy_xp_search_interval`: Buy XP搜索间隔 (秒)
- `max_buy_xp_search_attempts`: 最大搜索次数
- `buy_xp_threshold`: Buy XP按钮匹配阈值

### 4. 数据库设置 (`database`)

- `auto_save_on_stop`: 停止时是否自动保存
- `log_directory`: 日志保存目录

### 5. 键盘快捷键 (`keyboard_shortcuts`)

- `trigger_key`: 触发键 (默认: "d")

## 配置示例

### 修改匹配阈值
```json
{
  "matching_settings": {
    "threshold": 0.75
  }
}
```

### 修改检测区域
```json
{
  "matching_settings": {
    "fixed_regions": [
      {
        "id": 1,
        "name": "区域1",
        "coordinates": [700, 1250, 200, 150]
      }
    ]
  }
}
```

### 修改快捷键
```json
{
  "keyboard_shortcuts": {
    "trigger_key": "f",
    "exit_key": "q",
    "exit_modifier": "ctrl"
  }
}
```

## 注意事项

1. **坐标系统**: 所有坐标都基于屏幕左上角为原点 (0,0)
2. **颜色格式**: 使用十六进制颜色代码 (如 "#2c3e50")
3. **数值范围**: 
   - 匹配阈值: 0.5-1.0
   - 显示器索引: 1-4
   - 时间间隔: 正数
4. **文件编码**: 配置文件必须使用UTF-8编码

## 故障排除

### 配置文件加载失败
- 检查JSON语法是否正确
- 确保文件编码为UTF-8
- 检查文件权限

### 配置不生效
- 重启程序
- 检查配置项名称是否正确
- 查看控制台输出的配置加载信息

## 备份建议

建议在修改配置文件前先备份原始文件，以便在出现问题时快速恢复。
