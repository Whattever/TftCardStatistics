# 工具使用说明

## 概述

`tools` 文件夹包含独立的辅助工具，用于帮助确定游戏画面坐标和选择截取区域。

## 工具列表

### 1. 坐标查看器 (`coordinate_viewer.py`)

**用途**: 实时查看屏幕像素坐标，帮助确定关键位置的坐标值

**使用方法**:
```bash
# 基本使用
python tools/coordinate_viewer.py

# 指定显示器
python tools/coordinate_viewer.py --monitor 2

# 显示帮助
python tools/coordinate_viewer.py --help
```

**操作说明**:
- 移动鼠标查看实时坐标
- 按 `c` 复制当前坐标到剪贴板
- 按 `s` 保存当前截图
- 按 `h` 显示帮助信息
- 按 `Esc` 退出

**适用场景**: 需要记录多个关键位置坐标时

### 2. 区域选择器 (`region_picker.py`)

**用途**: 可视化选择屏幕截取区域，返回精确的坐标参数

**使用方法**:
```bash
# 基本使用
python tools/region_picker.py

# 指定显示器
python tools/region_picker.py --monitor 2

# 显示帮助
python tools/region_picker.py --help
```

**操作说明**:
- 点击并拖拽鼠标选择矩形区域
- 按 `r` 重新选择
- 按 `Enter` 确认选择
- 按 `h` 显示帮助
- 按 `Esc` 取消

**适用场景**: 需要确定截取区域时

## 完整工作流程

### 步骤1: 确定关键坐标
```bash
python tools/coordinate_viewer.py
```
- 移动鼠标到需要记录的位置
- 按 `c` 复制坐标到剪贴板
- 记录多个关键位置的坐标

### 步骤2: 选择截取区域
```bash
python tools/region_picker.py
```
- 点击并拖拽选择区域
- 按 `Enter` 确认
- 复制输出的命令行参数

### 步骤3: 使用坐标进行模板匹配
```bash
# 使用确定的区域坐标
python -m src.main --templates_dir tft_units --region 100,200,400,300 --show
```

## 工具特点

1. **独立性**: 每个工具都可以独立运行，不依赖主程序
2. **可视化**: 提供直观的图形界面，操作简单
3. **精确性**: 返回精确的像素坐标和区域参数
4. **灵活性**: 支持多显示器，可指定显示器索引
5. **用户友好**: 中文界面，详细的操作提示

## 注意事项

1. **游戏模式**: 独占全屏可能无法截图，建议使用无边框窗口模式
2. **DPI缩放**: Windows高DPI设置可能影响坐标，建议关闭缩放
3. **分辨率**: 确保游戏分辨率与模板图片一致
4. **依赖**: 需要安装 `opencv-python`, `numpy`, `mss` 等依赖包

## 故障排除

### 问题1: 截图显示黑色
**原因**: 游戏使用独占全屏模式
**解决**: 将游戏改为无边框窗口模式

### 问题2: 坐标不准确
**原因**: Windows DPI缩放影响
**解决**: 关闭显示设置中的缩放比例

### 问题3: 工具无法启动
**原因**: 依赖包未安装
**解决**: 运行 `pip install -r requirements.txt`

## 扩展功能

如需添加新的工具，请：
1. 在 `tools/` 文件夹中创建新的 `.py` 文件
2. 在 `tools/__init__.py` 中导入新工具
3. 更新此文档说明新工具的使用方法
