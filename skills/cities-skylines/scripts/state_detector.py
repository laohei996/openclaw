#!/usr/bin/env python3
"""
Cities Skylines 状态检测器
读取游戏内数据：金钱、人口、交通流量等
"""

import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import subprocess
import json

# Screen control 路径
SCREEN_CONTROL = Path(__file__).parent.parent.parent / "screen-control" / "scripts" / "screen_controller.py"


class GameStateDetector:
    """游戏状态检测"""
    
    # 游戏 UI 坐标（相对坐标，适配 4K）
    # 根据实际游戏调整
    STAT_REGIONS = {
        "money": (0.05, 0.96, 0.15, 0.99),        # 左下角金钱
        "population": (0.01, 0.01, 0.10, 0.04),   # 左上角人口
        "date": (0.02, 0.96, 0.08, 0.99),         # 左下角日期
    }
    
    def __init__(self):
        self.temp_dir = Path("C:/Users/admin/Desktop")
        self.last_screenshot = None
    
    def _screen_cmd(self, action: str, **kwargs) -> Dict:
        """调用 screen-control"""
        cmd = [sys.executable, str(SCREEN_CONTROL), action]
        
        for key, value in kwargs.items():
            if value is not None:
                cmd.append(f"--{key}")
                if value is not True:
                    cmd.append(str(value))
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        try:
            return json.loads(result.stdout)
        except:
            return {"status": "error"}
    
    def _region_to_string(self, region: Tuple[float, float, float, float]) -> str:
        """将相对坐标转换为屏幕坐标字符串（4K）"""
        x1, y1, x2, y2 = region
        
        # 假设 4K 分辨率
        screen_w, screen_h = 3840, 2160
        
        abs_x1 = int(x1 * screen_w)
        abs_y1 = int(y1 * screen_h)
        abs_x2 = int(x2 * screen_w)
        abs_y2 = int(y2 * screen_h)
        
        return f"{abs_x1},{abs_y1},{abs_x2},{abs_y2}"
    
    def capture_region(self, region_name: str) -> Optional[str]:
        """截取特定区域"""
        if region_name not in self.STAT_REGIONS:
            return None
        
        region = self.STAT_REGIONS[region_name]
        region_str = self._region_to_string(region)
        
        output_path = self.temp_dir / f"temp_{region_name}.png"
        
        result = self._screen_cmd("screenshot", 
                                  region=region_str,
                                  output=str(output_path))
        
        if result.get("status") == "success":
            return str(output_path)
        
        return None
    
    def read_stat_ocr(self, region_name: str) -> Optional[str]:
        """使用 OCR 读取统计数据
        
        注意：需要安装 pytesseract 和 Tesseract-OCR
        """
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            print("错误: 需要安装 pytesseract 和 pillow")
            print("pip install pytesseract pillow")
            return None
        
        # 截取区域
        image_path = self.capture_region(region_name)
        if not image_path:
            return None
        
        # OCR 识别
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='eng')
            
            # 清理文本
            text = text.strip()
            
            # 删除临时文件
            Path(image_path).unlink()
            
            return text
        except Exception as e:
            print(f"OCR 错误: {e}")
            return None
    
    def parse_money(self, text: str) -> Optional[int]:
        """解析金钱数值
        
        示例: "¥70,000" -> 70000
        """
        if not text:
            return None
        
        # 移除货币符号和逗号
        cleaned = re.sub(r'[¥$,]', '', text)
        
        # 提取数字
        match = re.search(r'[-+]?\d+', cleaned)
        if match:
            return int(match.group())
        
        return None
    
    def parse_population(self, text: str) -> Optional[int]:
        """解析人口数值"""
        if not text:
            return None
        
        # 移除逗号
        cleaned = re.sub(r',', '', text)
        
        # 提取数字
        match = re.search(r'\d+', cleaned)
        if match:
            return int(match.group())
        
        return None
    
    def get_game_stats(self) -> Dict:
        """获取游戏统计数据"""
        stats = {}
        
        # 读取金钱
        money_text = self.read_stat_ocr("money")
        if money_text:
            stats["money"] = self.parse_money(money_text)
            stats["money_raw"] = money_text
        
        # 读取人口
        pop_text = self.read_stat_ocr("population")
        if pop_text:
            stats["population"] = self.parse_population(pop_text)
            stats["population_raw"] = pop_text
        
        return stats
    
    def full_screenshot(self, output_path: str) -> bool:
        """全屏截图"""
        result = self._screen_cmd("screenshot", output=output_path)
        
        if result.get("status") == "success":
            self.last_screenshot = output_path
            return True
        
        return False
    
    def analyze_traffic(self, screenshot_path: Optional[str] = None) -> Dict:
        """分析交通状况（基于颜色检测）
        
        红色道路 = 拥堵
        绿色道路 = 畅通
        """
        if not screenshot_path:
            screenshot_path = self.last_screenshot
        
        if not screenshot_path or not Path(screenshot_path).exists():
            return {"error": "需要先截图"}
        
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            return {"error": "需要安装 pillow"}
        
        # 打开截图
        image = Image.open(screenshot_path).convert('RGB')
        arr = np.array(image)
        
        # 检测红色（拥堵）
        red_mask = (arr[:,:,0] > 150) & (arr[:,:,1] < 100) & (arr[:,:,2] < 100)
        red_pixels = np.sum(red_mask)
        
        # 检测绿色（畅通）
        green_mask = (arr[:,:,0] < 100) & (arr[:,:,1] > 150) & (arr[:,:,2] < 100)
        green_pixels = np.sum(green_mask)
        
        total_pixels = arr.shape[0] * arr.shape[1]
        
        return {
            "red_ratio": red_pixels / total_pixels,
            "green_ratio": green_pixels / total_pixels,
            "congestion_level": "high" if red_pixels > green_pixels else "low"
        }


def main():
    """测试入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cities Skylines 状态检测')
    parser.add_argument('command', choices=['stats', 'screenshot', 'money', 'population'])
    parser.add_argument('--output', default='game_state.png')
    
    args = parser.parse_args()
    
    detector = GameStateDetector()
    
    if args.command == 'stats':
        stats = detector.get_game_stats()
        print("游戏统计:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.command == 'screenshot':
        success = detector.full_screenshot(args.output)
        print(f"截图: {'成功' if success else '失败'} - {args.output}")
    
    elif args.command == 'money':
        text = detector.read_stat_ocr("money")
        value = detector.parse_money(text)
        print(f"金钱: {value} (原始: {text})")
    
    elif args.command == 'population':
        text = detector.read_stat_ocr("population")
        value = detector.parse_population(text)
        print(f"人口: {value} (原始: {text})")


if __name__ == '__main__':
    main()
