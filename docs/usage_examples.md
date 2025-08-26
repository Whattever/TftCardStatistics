# 使用示例

## 基本使用流程

### 1. 测试截图功能

首先测试程序是否能正确截取游戏画面：

```bash
# 测试模式：截取并显示5个固定区域
python -m src.main --test-capture
```

这个命令会：
- 截取5个预定义的TFT卡牌区域
- 在弹窗中显示每个截取的区域
- 按任意键关闭所有窗口

### 2. 使用固定区域进行模板匹配

#### 批量模板匹配
```bash
# 使用tft_units目录中的所有模板图片
python -m src.main --templates_dir tft_units --use-fixed-regions --show
```

这个命令会：
- 自动截取5个固定区域
- 将每个区域与tft_units目录中的所有模板进行匹配
- 显示匹配结果和可视化窗口
- 输出每个区域匹配到的模板名称

#### 单模板匹配
```bash
# 使用单个模板图片
python -m src.main --template tft_units/Ashe.png --use-fixed-regions --show
```

这个命令会：
- 自动截取5个固定区域
- 将每个区域与指定的模板图片进行匹配
- 显示匹配结果和可视化窗口
- 输出每个区域的匹配分数

### 3. 自定义区域匹配（可选）

如果需要匹配其他区域：

```bash
# 查看像素坐标
python tools/coordinate_viewer.py

# 选择截取区域
python tools/region_picker.py

# 使用自定义区域进行匹配
python -m src.main --templates_dir tft_units --region 100,200,400,300 --show
```

## 高级用法

### 调整匹配阈值

```bash
# 降低匹配阈值，提高匹配敏感度
python -m src.main --templates_dir tft_units --use-fixed-regions --threshold 0.7 --show

# 提高匹配阈值，提高匹配精度
python -m src.main --templates_dir tft_units --use-fixed-regions --threshold 0.95 --show
```

### 指定显示器

```bash
# 在多显示器环境下指定显示器
python -m src.main --templates_dir tft_units --use-fixed-regions --monitor 2 --show
```

### 组合使用

```bash
# 测试截图 + 批量匹配 + 可视化显示
python -m src.main --test-capture
python -m src.main --templates_dir tft_units --use-fixed-regions --show --threshold 0.85
```

## 输出示例

### 测试模式输出
```
=== 截图测试模式 ===
将截取以下5个固定区域:
  区域1: x=645, y=1240, w=250, h=185
  区域2: x=914, y=1240, w=250, h=185
  区域3: x=1183, y=1240, w=250, h=185
  区域4: x=1452, y=1240, w=250, h=185
  区域5: x=1721, y=1240, w=250, h=185

截取了 Region 1 (645,1240,250,185)
截取了 Region 2 (914,1240,250,185)
截取了 Region 3 (1183,1240,250,185)
截取了 Region 4 (1452,1240,250,185)
截取了 Region 5 (1721,1240,250,185)

按任意键关闭所有窗口...
```

### 固定区域匹配输出
```
=== 使用固定区域模式 ===
将截取5个固定区域进行模板匹配...

--- 区域1 (645,1240,250,185) ---
区域1 匹配到的模板: Ashe.png, Jinx.png

--- 区域2 (914,1240,250,185) ---
区域2 未匹配到任何模板

--- 区域3 (1183,1240,250,185) ---
区域3 匹配到的模板: Yasuo.png

--- 区域4 (1452,1240,250,185) ---
区域4 未匹配到任何模板

--- 区域5 (1721,1240,250,185) ---
区域5 匹配到的模板: Zed.png

按任意键关闭所有结果窗口...

=== 匹配结果总结 ===
区域1: Ashe.png, Jinx.png
区域3: Yasuo.png
区域5: Zed.png
```

## 故障排除

### 常见问题

1. **截图显示黑色**
   - 游戏使用独占全屏模式
   - 解决方案：将游戏改为无边框窗口模式

2. **匹配结果不准确**
   - 调整匹配阈值（--threshold参数）
   - 检查模板图片质量
   - 确认游戏分辨率与模板一致

3. **程序无法启动**
   - 检查依赖包是否安装完整
   - 运行 `pip install -r requirements.txt`

4. **坐标不准确**
   - 检查Windows DPI缩放设置
   - 使用坐标查看器重新确认坐标

### 调试建议

1. 先使用 `--test-capture` 确认截图功能正常
2. 使用 `--show` 参数查看可视化结果
3. 调整 `--threshold` 参数找到最佳匹配阈值
4. 检查控制台输出的详细匹配信息

