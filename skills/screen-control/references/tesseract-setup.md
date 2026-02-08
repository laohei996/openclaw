# Tesseract OCR 安装指南

## Windows 安装

### 1. 下载安装程序

访问: https://github.com/UB-Mannheim/tesseract/wiki

下载最新版本的安装程序（推荐 5.x 版本）

### 2. 安装 Tesseract

- 运行安装程序
- **重要**: 安装时勾选"Additional language data"
- 选择中文语言包: `Chinese - Simplified (chi_sim)`

默认安装路径: `C:\Program Files\Tesseract-OCR`

### 3. 配置环境变量

添加 Tesseract 到系统 PATH:

**方法 1: 临时设置**

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**方法 2: 永久设置**

1. 右键"此电脑" → 属性 → 高级系统设置
2. 环境变量 → 系统变量 → Path
3. 添加: `C:\Program Files\Tesseract-OCR`

### 4. 验证安装

```bash
tesseract --version
tesseract --list-langs
```

应该看到 `chi_sim` 和 `eng` 在语言列表中。

## 手动下载语言包

如果安装时未包含中文语言包：

1. 下载语言包:
   - 简体中文: https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
   - 繁体中文: https://github.com/tesseract-ocr/tessdata/raw/main/chi_tra.traineddata

2. 放入 Tesseract 安装目录的 `tessdata` 文件夹:
   ```
   C:\Program Files\Tesseract-OCR\tessdata\chi_sim.traineddata
   ```

## 测试 OCR

创建测试脚本:

```python
import pytesseract
from PIL import Image

# 配置 Tesseract 路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 测试英文
img = Image.open('test_en.png')
text = pytesseract.image_to_string(img, lang='eng')
print(text)

# 测试中文
img = Image.open('test_cn.png')
text = pytesseract.image_to_string(img, lang='chi_sim')
print(text)
```

## 常见问题

### 找不到 tesseract 命令

确保已添加到 PATH，或在脚本中显式指定路径。

### 中文识别率低

1. 确保已安装 `chi_sim` 语言包
2. 使用 `lang='chi_sim+eng'` 混合识别
3. 预处理图像（二值化、去噪）

### 性能优化

- 使用 `--psm` 参数指定页面分割模式
- 限定搜索区域减少处理时间
- 缓存常用模板图像
