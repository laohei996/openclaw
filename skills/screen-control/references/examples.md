# Screen Control - 使用示例

## 基础点击

### 通过文字点击

```bash
python scripts/screen_controller.py click --target "确定" --method text
python scripts/screen_controller.py click --target "Start Game" --method text
```

### 通过图像点击

```bash
python scripts/screen_controller.py click --target "button.png" --method image
```

### 通过坐标点击

```bash
# 绝对坐标（1920x1080 分辨率）
python scripts/screen_controller.py click --target "960,540" --method coord

# 相对坐标（0-1 比例，屏幕中心）
python scripts/screen_controller.py click --target "0.5,0.5" --method coord
```

### 自动识别

```bash
# 自动判断是文字、图像还是坐标
python scripts/screen_controller.py click --target "开始"
python scripts/screen_controller.py click --target "icon.png"
python scripts/screen_controller.py click --target "100,200"
```

## 高级点击

### 双击

```bash
python scripts/screen_controller.py click --target "文件夹" --clicks 2
```

### 右键点击

```bash
python scripts/screen_controller.py click --target "桌面" --button right
```

### 限定区域搜索

```bash
# 只在屏幕左上角 800x600 区域搜索
python scripts/screen_controller.py click --target "按钮" --region "0,0,800,600"
```

## 拖拽操作

### 文字到文字

```bash
python scripts/screen_controller.py drag --start "文件" --end "回收站"
```

### 坐标到坐标

```bash
python scripts/screen_controller.py drag --start "100,100" --end "500,500" --duration 1.0
```

### 图像到坐标

```bash
python scripts/screen_controller.py drag --start "icon.png" --end "0.9,0.9" --method auto
```

## 截图

### 全屏截图

```bash
python scripts/screen_controller.py screenshot --output "full.png"
```

### 区域截图

```bash
python scripts/screen_controller.py screenshot --region "100,100,800,600" --output "region.png"
```

## 查找位置

### 查找文字

```bash
python scripts/screen_controller.py find --target "设置" --method text
# 输出: {"status": "success", "action": "find", "location": [1234, 567]}
```

### 查找图像

```bash
python scripts/screen_controller.py find --target "button.png" --method image
```

## 调试模式

启用调试信息：

```bash
python scripts/screen_controller.py click --target "按钮" --debug
```

## 分辨率适配

脚本会自动检测当前屏幕分辨率并适配坐标：

- **相对坐标** (0-1): 始终相对于当前分辨率
  - `0.5,0.5` = 屏幕中心
  - `0,0` = 左上角
  - `1,1` = 右下角

- **绝对坐标**: 从默认 1920x1080 自动缩放到当前分辨率
  - 如果当前是 2560x1440，坐标 `960,540` 会自动缩放为 `1280,720`

## 常见场景

### 游戏自动化

```bash
# 点击"开始游戏"按钮
python scripts/screen_controller.py click --target "start_button.png"

# 拖拽技能到快捷栏
python scripts/screen_controller.py drag --start "skill_icon.png" --end "0.5,0.9"
```

### 办公自动化

```bash
# 打开文件菜单
python scripts/screen_controller.py click --target "文件"

# 双击打开文档
python scripts/screen_controller.py click --target "document.png" --clicks 2

# 右键保存
python scripts/screen_controller.py click --target "图片" --button right
```

## 注意事项

1. **安全机制**: 鼠标移动到屏幕左上角可中断操作（pyautogui.FAILSAFE）
2. **Tesseract**: OCR 需要安装 Tesseract-OCR ([下载](https://github.com/UB-Mannheim/tesseract/wiki))
3. **中文识别**: 需要下载中文语言包 `chi_sim.traineddata`
4. **图像匹配**: 模板图像需要与实际界面大小一致
5. **分辨率**: 建议使用相对坐标（0-1）以适配不同分辨率
