# 故障排除指南

## 常见问题及解决方案

### 1. 导入错误 (ImportError)

**错误信息：**
```
ImportError: attempted relative import with no known parent package
```

**原因：** 直接运行 `python src/main.py` 导致的相对导入问题

**解决方案：**
- 使用启动脚本：`python run.py [参数]`
- 使用模块方式：`python -m src.main [参数]`

### 2. 模块未找到 (ModuleNotFoundError)

**错误信息：**
```
ModuleNotFoundError: No module named 'src'
```

**原因：** Python无法找到src模块

**解决方案：**
- 确保在项目根目录下运行命令
- 使用 `python -m src.main` 而不是 `python src/main.py`

### 3. 依赖包缺失

**错误信息：**
```
ModuleNotFoundError: No module named 'cv2'
ModuleNotFoundError: No module named 'mss'
```

**解决方案：**
```bash
pip install -r requirements.txt
```

### 4. 截图失败

**可能原因：**
- 游戏使用独占全屏模式
- 权限不足
- 显示器索引错误

**解决方案：**
- 将游戏设置为无边框窗口模式
- 以管理员身份运行程序
- 检查 `--monitor` 参数设置

### 5. 模板匹配失败

**可能原因：**
- 阈值设置过高
- 模板图片与游戏画面不匹配
- 游戏分辨率与模板不匹配

**解决方案：**
- 降低匹配阈值：`--threshold 0.7`
- 确保模板图片清晰且与游戏画面一致
- 检查游戏分辨率设置

## 正确的运行方式

### 推荐方式：使用启动脚本
```bash
# 查看帮助
python run.py --help

# 测试截图
python run.py --test-capture

# 模板匹配
python run.py --templates_dir tft_units --use-fixed-regions --show
```

### 自动截取工具
```bash
# 自动截取FIXED_REGIONS区域并去重保存
python tools/auto_capture.py

# Windows用户也可以双击运行
tools/auto_capture.bat
```

### 备选方式：使用模块方式
```bash
# 查看帮助
python -m src.main --help

# 测试截图
python -m src.main --test-capture

# 模板匹配
python -m src.main --templates_dir tft_units --use-fixed-regions --show
```

## 调试技巧

1. **使用 `--show` 参数**：显示匹配结果的可视化窗口
2. **降低阈值**：使用 `--threshold 0.7` 进行更宽松的匹配
3. **测试截图**：先运行 `--test-capture` 确认截图功能正常
4. **检查坐标**：使用 `tools/coordinate_viewer.py` 验证坐标设置

## 获取帮助

如果问题仍然存在，请：
1. 检查错误信息的完整内容
2. 确认Python版本和依赖包版本
3. 尝试在项目根目录下运行命令
4. 查看项目的GitHub Issues页面
