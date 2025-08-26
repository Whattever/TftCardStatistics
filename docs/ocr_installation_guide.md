# OCR数字识别功能安装指南

## 概述

OCR（光学字符识别）功能能够自动识别指定区域的数字（0-10），并将其与模板匹配结果关联存储。本指南将帮助您安装和配置OCR功能。

## 系统要求

- Python 3.7+
- 足够的磁盘空间（约100MB用于Tesseract引擎）
- 支持的操作系统：Windows、macOS、Linux

## 安装步骤

### 1. 安装Python依赖

```bash
# 安装pytesseract库
pip install pytesseract

# 或者更新requirements.txt后安装
pip install -r requirements.txt
```

### 2. 安装Tesseract OCR引擎

#### Windows用户

1. **下载Tesseract安装包**
   - 访问 [UB-Mannheim的Tesseract页面](https://github.com/UB-Mannheim/tesseract/wiki)
   - 下载适合您系统的安装包（推荐64位版本）

2. **安装Tesseract**
   - 运行下载的安装包
   - 选择安装路径（记住这个路径，后面需要配置）
   - 确保勾选"Additional language data"以支持更多语言
   - 完成安装

3. **配置环境变量**
   - 将Tesseract安装目录添加到系统PATH
   - 或者在代码中指定Tesseract路径

#### macOS用户

```bash
# 使用Homebrew安装
brew install tesseract

# 或者使用MacPorts
sudo port install tesseract
```

#### Linux用户

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# CentOS/RHEL
sudo yum install tesseract

# Arch Linux
sudo pacman -S tesseract
```

### 3. 验证安装

运行测试脚本验证OCR功能：

```bash
python test_ocr.py
```

如果看到"🎉 所有OCR测试通过！"消息，说明安装成功。

## 配置说明

### Windows用户特殊配置

如果您在Windows上遇到Tesseract路径问题，可以在代码中指定路径：

```python
from src.ocr_module import NumberOCR

# 指定Tesseract可执行文件路径
ocr = NumberOCR(tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```

### 自定义OCR区域

默认OCR识别区域为 (367, 1179, 20, 30)。如需修改，请编辑以下文件：

1. **连续监控模式**: 修改 `src/main.py` 中的 `OCR_REGION` 变量
2. **单次运行模式**: 修改 `src/main.py` 中 `use_fixed_regions` 部分的 `OCR_REGION` 变量

## 故障排除

### 常见问题

#### 1. ImportError: No module named 'pytesseract'
```bash
# 解决方案：安装pytesseract
pip install pytesseract
```

#### 2. TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```bash
# 解决方案：安装Tesseract OCR引擎
# Windows: 下载并安装Tesseract
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

#### 3. OCR识别准确率低
- 确保目标区域图像清晰
- 调整图像预处理参数
- 检查目标区域是否被遮挡

#### 4. Windows上路径问题
```python
# 在代码中明确指定Tesseract路径
ocr = NumberOCR(tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```

### 调试模式

启用OCR调试模式可以保存中间处理图像：

```python
from src.ocr_module import NumberOCR

ocr = NumberOCR()
# 启用调试模式，保存处理前后的图像
result = ocr.debug_ocr(image, region, save_debug=True)
```

调试图像将保存为：
- `debug_region_original.png`: 原始区域图像
- `debug_region_processed.png`: 预处理后的图像

## 性能优化

### 1. 图像预处理优化
- 调整 `scale_factor` 参数（默认3倍放大）
- 修改高斯模糊核大小
- 调整形态学操作参数

### 2. Tesseract配置优化
```python
# 自定义Tesseract配置
config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
```

参数说明：
- `--oem 3`: 使用LSTM OCR引擎
- `--psm 7`: 单行文本模式
- `-c tessedit_char_whitelist=0123456789`: 只识别数字0-9

## 使用示例

### 基本使用

```python
from src.ocr_module import NumberOCR

# 创建OCR实例
ocr = NumberOCR()

# 识别图像中的数字
result = ocr.recognize_number(image)
if result is not None:
    print(f"识别到数字: {result}")
```

### 区域识别

```python
# 从完整图像中截取指定区域并识别
result = ocr.recognize_number_from_region(full_image, (360, 1173, 27, 36))
```

### 集成到主程序

OCR功能已自动集成到以下模式中：
- `--continuous`: 连续监控模式
- `--use-fixed-regions`: 固定区域模式

每次触发匹配时，程序会自动：
1. 执行模板匹配
2. 截取OCR区域 (360, 1173, 27, 36)
3. 识别数字
4. 将结果存储到数据库

## 技术支持

如果遇到问题，请：

1. 检查依赖是否正确安装
2. 运行测试脚本 `python test_ocr.py`
3. 查看错误日志和调试信息
4. 确认Tesseract安装和配置

## 更新日志

- **v1.0**: 初始OCR功能实现
- 支持数字0-10识别
- 自动图像预处理优化
- 集成到主程序流程
- 数据库存储支持
