# TFT卡牌统计工具

一个用于识别全屏游戏界面内特定像素区域的图片并将其与预设图片匹配的工具。

## 功能特性

- 🖥️ 全屏截图与区域裁剪
- 🔍 模板图片匹配识别
- 📁 批量模板目录匹配
- 🎯 可视化坐标查看与区域选择
- 📊 匹配结果可视化显示
- 🔄 持续监控模式（新增）
- ⌨️ 快捷键触发截图（新增）
- 📈 数据统计与记录（新增）
- 🔢 OCR数字识别（新增）

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 准备模板图片
将需要匹配的图片模板放入 `tft_units/` 文件夹

### 3. 运行程序
有两种运行方式：

**方式1：使用启动脚本（推荐）**
```bash
# 测试模式：截取并显示5个固定区域
python run.py --test-capture

# 持续监控模式（推荐用于游戏中进行实时监控）
python run.py --continuous

# 查看帮助信息
python run.py --help
```

**方式2：使用模块方式**
```bash
# 测试模式：截取并显示5个固定区域
python -m src.main --test-capture
```

**注意**：不要直接运行 `python src/main.py`，这会导致导入错误。

### 4. 使用固定区域进行模板匹配
```bash
# 批量匹配所有5个固定区域
python run.py --templates_dir tft_units --use-fixed-regions --show

# 单模板匹配所有5个固定区域
python run.py --template tft_units/example.png --use-fixed-regions --show
```

### 5. 自定义区域匹配（可选）
```bash
# 查看像素坐标
python tools/coordinate_viewer.py

# 选择截取区域
python tools/region_picker.py

# 使用自定义区域进行匹配
python run.py --templates_dir tft_units --region 100,200,400,300 --show
```

### 6. 自动截取和去重保存
```bash
# 自动截取FIXED_REGIONS区域并去重保存
python tools/auto_capture.py

# Windows用户也可以双击运行
tools/auto_capture.bat
```

### 7. 持续监控模式（新增）
```bash
# 启动持续监控模式
python run.py --continuous

# 或使用批处理文件（Windows）
run_continuous.bat

# 自定义参数启动
python run.py --continuous --templates_dir my_templates --threshold 0.7 --show
```

**快捷键说明：**
- **D**: 触发截图和模板匹配
- **Ctrl+F1**: 退出程序

### 8. 数据统计功能（新增）
```bash
# 启用统计功能（非连续模式）
python run.py --templates_dir tft_units --use-fixed-regions --enable-stats

# 查看统计数据
python tools/stats_viewer.py

# 查看特定会话统计
python tools/stats_viewer.py --session 1

# 列出所有会话
python tools/stats_viewer.py --list-sessions

# 导出数据到CSV（使用英文标题，避免乱码）
python tools/stats_viewer.py --export stats.csv

# 或使用批处理文件（Windows）
tools/view_stats.bat
```

### 9. OCR数字识别功能（新增）
```bash
# 测试OCR功能
python test_ocr.py

# 连续监控模式（自动启用OCR）
python run.py --continuous

# 单次运行（自动启用OCR）
python run.py --templates_dir tft_units --use-fixed-regions --enable-stats
```

### 10. 新CSV导出功能（新增）
```bash
# 导出新的CSV格式数据（包含特定字段）
python tools/stats_viewer.py --export-new export_new.csv

# 导出的CSV包含以下信息：
# - matches表: capture_sequence, unit_name, cost, ocr_number
# - template_stats表: id, unit_name, cost, total_matches
```

**OCR功能说明：**
- 自动识别坐标 (360, 1173, 27, 36) 区域的数字（0-10）
- 将OCR结果与模板匹配结果关联存储
- 支持图像预处理优化识别准确率
- 结果存储在数据库中，支持统计分析和导出

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
│   ├── coordinate_viewer.py  # 坐标查看器
│   ├── region_picker.py      # 区域选择器
│   ├── auto_capture.py       # 自动截取和去重保存
│   ├── stats_viewer.py       # 统计数据查看器
│   └── view_stats.bat        # 统计查看工具批处理文件
├── tft_units/            # 模板图片目录
├── docs/                 # 文档
├── test_ocr.py           # OCR功能测试脚本
└── requirements.txt      # 依赖包列表
```

## 详细文档

- [坐标确定指南](docs/coordinate_guide.md)
- [工具使用说明](docs/tools_usage.md)
- [使用示例](docs/usage_examples.md)
- [持续监控模式指南](docs/continuous_mode_guide.md)


## 命令行参数

### 主程序参数
- `--template`: 单个模板图片路径
- `--templates_dir`: 模板图片目录路径
- `--region`: 截取区域 (x,y,宽度,高度)
- `--monitor`: 显示器索引 (默认: 1)
- `--threshold`: 匹配阈值 (0-1, 默认: 0.9)
- `--show`: 显示可视化结果
- `--test-capture`: 测试模式，截取并显示5个固定区域
- `--use-fixed-regions`: 使用预定义的5个TFT卡牌区域进行匹配
- `--enable-stats`: 启用数据统计记录功能


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

这些坐标基于特定游戏分辨率设计，如需调整请修改 `src/main.py` 中的 `FIXED_REGIONS` 变量。

## 注意事项

1. **游戏模式**: 独占全屏无法截图，请使用无边框窗口模式
2. **分辨率**: 确保游戏分辨率与模板图片一致
3. **DPI缩放**: Windows高DPI设置可能影响坐标精度
4. **固定区域**: 使用 `--use-fixed-regions` 时，程序会自动截取所有5个预定义区域
5. **数据统计**: 统计功能会自动创建 `tft_stats.db` 数据库文件，记录所有匹配历史
6. **OCR识别**: 需要安装Tesseract OCR引擎和pytesseract库，Windows用户需要配置Tesseract路径

## 许可证

MIT License
