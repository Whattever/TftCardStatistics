# TFT卡牌统计工具

一个用于识别全屏游戏界面内特定像素区域的图片并将其与预设图片匹配的工具。支持实时监控、OCR识别、数据统计和GUI界面。

## 功能特性

- 🖥️ 全屏截图与区域裁剪
- 🔍 模板图片匹配识别
- 📁 批量模板目录匹配
- 📊 匹配结果可视化显示
- 📈 数据统计与记录（新增）
- 🖱️ GUI图形界面（新增）
- ⚙️ 配置文件支持（新增）
- 🎮 自动阶段检测（新增）

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行程序
有三种运行方式：

**方式1：使用GUI界面（推荐）**
```bash
# 启动图形界面
python gui_launcher.py

# 或使用批处理文件（Windows）
run_gui.bat
```

**方式2：使用release版本可执行文件**

**注意**：不要直接运行 `python src/main.py`，这会导致导入错误。

### 3. 配置选项

程序支持通过 `config.json` 文件进行配置：

### 匹配设置
- `threshold`: 模板匹配阈值 (默认: 0.68)
- `monitor_index`: 显示器索引 (默认: 1)
- `enable_ocr`: 是否启用OCR识别 (默认: true)
- `base_resolution`: 基础分辨率设置（不要改）
- `fixed_regions`: 5个固定截取区域配置
- `ocr_regions`: OCR识别区域配置

### 自动识别设置
- `stage_monitor_interval`: 阶段检测间隔 (默认: 0.5秒)
- `buy_xp_search_interval`: 购买经验搜索间隔 (默认: 2.0秒)
- `max_buy_xp_search_attempts`: 最大搜索尝试次数 (默认: 30)
- `buy_xp_threshold`: 购买经验按钮识别阈值 (默认: 0.7)

### 数据库设置
- `auto_save_on_stop`: 停止时自动保存 (默认: true)
- `log_directory`: 日志目录 (默认: "log")

### 快捷键设置
- `trigger_key`: 触发键 (默认: "d")

## 项目结构

```
TftCardStatistics/
├── src/                    # 核心功能模块
│   ├── capture.py         # 屏幕截图功能
│   ├── matching.py        # 模板匹配功能
│   ├── database.py        # 数据统计数据库
│   ├── ocr_module.py      # OCR数字识别模块
│   └── main.py           # 主程序入口
├── tools/                 # 独立工具
│   ├── Buy_XP.png         # 阶段识别的图片模板
├── tft_units/            # 模板图片目录
├── docs/                 # 文档
├── test_ocr.py           # OCR功能测试脚本
├── gui_launcher.py       # GUI启动器
├── run_gui.py            # GUI运行脚本
├── config.json           # 配置文件
└── requirements.txt      # 依赖包列表
```

## 详细文档

- [配置说明文档](docs/CONFIG_README.md)

## 命令行参数

### 主程序参数
- `--template`: 单个模板图片路径
- `--templates_dir`: 模板图片目录路径
- `--region`: 截取区域 (x,y,宽度,高度)
- `--monitor`: 显示器索引 (默认: 1)
- `--threshold`: 匹配阈值 (0-1, 默认: 0.68)
- `--show`: 显示可视化结果
- `--test-capture`: 测试模式，截取并显示5个固定区域
- `--use-fixed-regions`: 使用预定义的5个TFT卡牌区域进行匹配
- `--enable-stats`: 启用数据统计记录功能
- `--continuous`: 启动持续监控模式

### 工具参数
- `--monitor`: 指定显示器索引
- `--export-new`: 导出新的CSV格式数据（包含特定字段）
- `--help`: 显示帮助信息

## 固定截取区域

程序预定义了5个TFT卡牌截取区域，每个区域尺寸为250×185像素：

- **区域1**: (645, 1240, 250, 185)
- **区域2**: (914, 1240, 250, 185)  
- **区域3**: (1183, 1240, 250, 185)
- **区域4**: (1452, 1240, 250, 185)
- **区域5**: (1721, 1240, 250, 185)

这些坐标基于特定游戏分辨率设计，可通过 `config.json` 文件进行调整。

## OCR识别区域

程序配置了以下OCR识别区域：

- **等级检测区域**: (360, 1173, 27, 36) - 用于识别当前等级
- **阶段检测区域**: (1023, 10, 127, 35) - 用于识别当前阶段

## 新增功能

### 自动阶段检测
- 实时监控游戏阶段变化
- 自动记录阶段信息到数据库
- 支持阶段统计和分析

### 自动购买经验检测
- 自动识别购买经验按钮
- 可配置的搜索间隔和尝试次数
- 支持自定义识别阈值

### GUI界面
- 图形化配置界面
- 实时状态显示
- 一键启动和停止
- 参数可视化调整

## 注意事项

1. **游戏模式**: 独占全屏无法截图，请使用无边框窗口模式
2. **分辨率**: 确保游戏分辨率与模板图片一致
3. **DPI缩放**: Windows高DPI设置可能影响坐标精度
4. **固定区域**: 使用 `--use-fixed-regions` 时，程序会自动截取所有5个预定义区域
5. **数据统计**: 统计功能会自动创建 `tft_stats.db` 数据库文件，记录所有匹配历史
6. **OCR识别**: 需要安装Tesseract OCR引擎和pytesseract库，Windows用户需要配置Tesseract路径
7. **配置文件**: 修改 `config.json` 后需要重启程序才能生效
8. **GUI模式**: GUI模式下支持实时参数调整和状态监控

## 许可证

MIT License
