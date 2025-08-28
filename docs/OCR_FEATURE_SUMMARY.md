# OCR数字识别功能实现总结

## 功能概述

成功为TFT卡牌统计工具新增了OCR数字识别功能，能够自动识别指定区域 (367, 1179, 20, 30) 内的数字（0-10），并将识别结果与模板匹配结果关联存储到数据库中。

## 新增功能特性

### 🔢 自动数字识别
- **区域识别**: 自动截取坐标 (360, 1173, 27, 36) 的区域
- **数字范围**: 支持识别0-10的阿拉伯数字
- **实时识别**: 每次D触发匹配时自动执行OCR识别
- **结果关联**: OCR结果与模板匹配结果自动关联

### 🖼️ 图像预处理优化
- **灰度转换**: 自动转换为灰度图像提高识别率
- **图像放大**: 3倍放大优化小字体识别
- **噪声去除**: 高斯模糊和形态学操作去除噪点
- **阈值处理**: 自适应阈值突出数字特征

### 💾 数据存储集成
- **数据库扩展**: 新增OCR字段存储识别结果
- **关联存储**: OCR结果与匹配记录关联存储
- **统计支持**: 支持OCR结果的统计分析和导出
- **向后兼容**: 不影响现有数据库结构

## 技术实现

### 1. OCR模块 (`src/ocr_module.py`)
- **NumberOCR类**: 核心OCR识别类
- **图像预处理**: 多步骤图像优化流程
- **Tesseract集成**: 使用开源OCR引擎
- **错误处理**: 完善的异常处理和日志记录

### 2. 数据库扩展 (`src/database.py`)
- **字段扩展**: 新增 `level` 和 `ocr_confidence` 字段
- **数据关联**: OCR结果与匹配记录关联存储
- **统计支持**: 支持OCR结果的统计查询

### 3. 主程序集成 (`src/main.py`)
- **自动集成**: 连续监控和单次运行模式自动启用OCR
- **流程优化**: 在模板匹配后自动执行OCR识别
- **结果展示**: 实时显示OCR识别结果

### 4. 统计工具更新 (`tools/stats_viewer.py`)
- **数据导出**: CSV导出包含OCR结果
- **字段支持**: 支持OCR字段的查询和显示

## 使用方法

### 启用OCR功能

#### 连续监控模式（自动启用）
```bash
python run.py --continuous
```

#### 单次运行模式（自动启用）
```bash
python run.py --templates_dir tft_units --use-fixed-regions --enable-stats
```

### 测试OCR功能
```bash
python test_ocr.py
```

### 查看OCR结果
```bash
# 查看统计数据（包含OCR结果）
python tools/stats_viewer.py

# 导出数据（包含OCR结果）
python tools/stats_viewer.py --export stats.csv
```

## 安装要求

### Python依赖
```bash
pip install pytesseract
```

### 系统依赖
- **Windows**: 安装Tesseract OCR引擎
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## 配置说明

### OCR区域配置
默认OCR识别区域为 (360, 1173, 27, 36)，如需修改：

1. **连续监控模式**: 修改 `src/main.py` 中的 `OCR_REGION` 变量
2. **单次运行模式**: 修改 `src/main.py` 中 `use_fixed_regions` 部分的 `OCR_REGION` 变量

### Windows用户配置
如果遇到Tesseract路径问题：
```python
from src.ocr_module import NumberOCR

# 指定Tesseract可执行文件路径
ocr = NumberOCR(tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```

## 工作流程

### 1. 触发匹配
- 用户按D键触发截图和匹配
- 程序截取5个固定TFT卡牌区域
- 执行模板匹配

### 2. OCR识别
- 自动截取OCR区域 (360, 1173, 27, 36)
- 执行图像预处理优化
- 使用Tesseract识别数字

### 3. 结果存储
- 将OCR结果添加到所有匹配详情中
- 存储到数据库的 `level` 和 `ocr_confidence` 字段
- 支持后续统计分析和导出

### 4. 结果展示
- 实时显示OCR识别结果
- 在统计摘要中包含OCR信息
- 支持CSV导出包含OCR数据

## 性能特点

### 识别准确率
- **图像预处理**: 多步骤优化提高识别率
- **参数调优**: 针对数字识别优化的Tesseract参数
- **范围验证**: 只接受0-10范围内的有效结果

### 处理速度
- **异步处理**: OCR识别不阻塞主程序运行
- **图像优化**: 预处理减少Tesseract处理时间
- **缓存机制**: 避免重复的图像处理

### 资源占用
- **内存优化**: 只处理必要的图像区域
- **磁盘空间**: 约100MB用于Tesseract引擎
- **CPU使用**: 轻量级图像处理，影响最小

## 实际应用场景

### 1. 游戏数据分析
- 识别游戏中的数字标识
- 关联卡牌匹配和数字信息
- 分析游戏策略和数字规律

### 2. 自动化监控
- 实时监控游戏状态
- 自动记录数字变化
- 生成详细的游戏日志

### 3. 数据挖掘
- 分析数字出现频率
- 研究游戏平衡性
- 优化游戏策略

## 故障排除

### 常见问题

#### 1. OCR识别失败
- 检查Tesseract是否正确安装
- 验证目标区域是否清晰可见
- 调整图像预处理参数

#### 2. 识别准确率低
- 确保目标区域图像质量
- 检查是否有遮挡或干扰
- 调整OCR区域坐标

#### 3. 性能问题
- 优化图像预处理参数
- 调整Tesseract配置
- 检查系统资源使用

### 调试方法

启用OCR调试模式：
```python
result = ocr.debug_ocr(image, region, save_debug=True)
```

调试图像将保存为：
- `debug_region_original.png`: 原始区域图像
- `debug_region_processed.png`: 预处理后的图像

## 未来扩展

### 可能的功能增强
- **多区域识别**: 支持识别多个不同区域的数字
- **字符识别**: 扩展支持字母和符号识别
- **机器学习**: 集成深度学习模型提高识别率
- **实时优化**: 基于识别结果的动态参数调整

### 性能优化
- **并行处理**: 多线程OCR识别
- **缓存优化**: 智能缓存识别结果
- **参数自适应**: 基于图像特征的自动参数调整

## 总结

成功实现了完整的OCR数字识别功能，包括：

1. **自动识别**: 无需手动干预，自动识别指定区域的数字
2. **智能预处理**: 多步骤图像优化提高识别准确率
3. **完整集成**: 与现有功能无缝集成，不影响原有使用方式
4. **数据关联**: OCR结果与模板匹配结果自动关联存储
5. **统计分析**: 支持OCR结果的统计分析和数据导出

这些新功能为TFT卡牌统计工具增加了强大的数字识别能力，用户可以深入了解游戏中的数字信息，为游戏策略提供更全面的数据支持。

## 文件清单

新增和修改的文件：
- `src/ocr_module.py` - OCR核心模块
- `src/database.py` - 数据库扩展（OCR字段）
- `src/main.py` - 主程序集成OCR功能
- `tools/stats_viewer.py` - 统计工具OCR支持
- `test_ocr.py` - OCR功能测试脚本
- `requirements.txt` - 添加OCR依赖
- `docs/ocr_installation_guide.md` - OCR安装指南
- `README.md` - 更新功能说明