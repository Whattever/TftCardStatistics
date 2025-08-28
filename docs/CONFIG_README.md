# TFT卡牌统计系统配置文件说明

## 概述

`config.json` 文件包含了TFT卡牌统计系统的所有配置参数，通过修改此文件可以自定义系统的行为，而无需修改源代码。

## 配置文件结构

### 1. GUI设置 (`gui_settings`)

#### 窗口配置 (`window`)
- `title`: 窗口标题
- `geometry`: 窗口尺寸 (宽x高)
- `background_color`: 主窗口背景颜色

#### 控制面板 (`control_panel`)
- `background_color`: 控制面板背景颜色

#### 表格设置 (`table`)
- `background_color`: 表格背景颜色
- `label_colors`: 标签颜色配置
  - `level`: Level按钮颜色
  - `count`: 计数标签颜色
  - `selected`: 选中状态颜色

#### 图表设置 (`charts`)
- `background_color`: 图表背景颜色
- `text_color`: 图表文字颜色
- `pie_chart`: 饼图配置
  - `figsize`: 图表尺寸 [宽度, 高度]
  - `colors`: 费用颜色列表
- `line_chart`: 直方图配置
  - `figsize`: 图表尺寸 [宽度, 高度]
  - `cost_colors`: 各费用对应的颜色

#### 日志设置 (`log`)
- `background_color`: 日志区域背景颜色
- `text_color`: 日志文字颜色
- `max_lines`: 最大日志行数

### 2. 匹配设置 (`matching_settings`)

#### 基本参数
- `threshold`: 图片匹配阈值 (0.5-1.0)
- `templates_directory`: 模板图片目录
- `monitor_index`: 显示器索引 (1-4)
- `enable_ocr`: 是否启用OCR功能

#### 固定区域 (`fixed_regions`)
定义5个TFT卡牌检测区域，每个区域包含：
- `id`: 区域编号
- `name`: 区域名称
- `coordinates`: 坐标 [x, y, 宽度, 高度]

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
- `exit_key`: 退出键 (默认: "f1")
- `exit_modifier`: 退出修饰键 (默认: "ctrl")

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
