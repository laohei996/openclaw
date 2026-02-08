# Screen Control Skill - 安装说明

## 快速安装

### 1. Python 依赖

```bash
pip install pyautogui opencv-python pillow pytesseract numpy
```

### 2. Tesseract OCR（可选，用于文字识别）

**下载地址**: https://github.com/UB-Mannheim/tesseract/wiki

**安装步骤**:

1. 下载最新版 Tesseract-OCR 安装程序
2. 运行安装程序
3. **重要**: 勾选 "Additional language data"
4. 选择中文语言包: `Chinese - Simplified (chi_sim)`
5. 添加到系统 PATH: `C:\Program Files\Tesseract-OCR`

**验证安装**:

```bash
tesseract --version
tesseract --list-langs
```

### 3. 测试 Skill

```bash
# 截图测试
python C:\Users\admin\openclaw\skills\screen-control\scripts\screen_controller.py screenshot --output test.png

# 点击屏幕中心
python C:\Users\admin\openclaw\skills\screen-control\scripts\screen_controller.py click --target "0.5,0.5"
```

## 依赖说明

- **pyautogui**: 鼠标键盘控制
- **opencv-python**: 图像模板匹配
- **pillow**: 图像处理
- **pytesseract**: OCR 文字识别（需要 Tesseract-OCR）
- **numpy**: 数值计算

## 可选配置

### 配置 Tesseract 路径（如果未加入 PATH）

在脚本开头添加：

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 权限要求

- **屏幕截图**: 无需额外权限
- **鼠标控制**: 无需额外权限
- **全屏游戏**: 可能需要管理员权限
