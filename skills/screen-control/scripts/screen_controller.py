#!/usr/bin/env python3
"""
Screen Controller - 混合方案的屏幕控制工具
支持 OCR 文字识别、图像模板匹配、相对坐标点击、拖拽等操作
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Tuple, Optional, List
import json

try:
    import pyautogui
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
except ImportError as e:
    print(f"错误：缺少依赖库 {e.name}")
    print("请运行：pip install pyautogui opencv-python pillow pytesseract")
    sys.exit(1)

# 配置 pyautogui 安全设置
pyautogui.FAILSAFE = True  # 鼠标移到左上角可中断
pyautogui.PAUSE = 0.1  # 每次操作间隔


class ScreenController:
    """屏幕控制器"""
    
    def __init__(self, confidence: float = 0.8, debug: bool = False):
        """
        初始化控制器
        
        Args:
            confidence: 图像匹配置信度阈值 (0.0-1.0)
            debug: 是否启用调试模式（保存中间结果）
        """
        self.confidence = confidence
        self.debug = debug
        self.screen_size = pyautogui.size()
        
    def get_screen_resolution(self) -> Tuple[int, int]:
        """获取当前屏幕分辨率"""
        return self.screen_size
    
    def normalize_coordinates(self, x: float, y: float, 
                            ref_width: int = 1920, 
                            ref_height: int = 1080) -> Tuple[int, int]:
        """
        将参考分辨率下的坐标转换为当前分辨率
        
        Args:
            x, y: 参考分辨率下的坐标（可以是像素或 0-1 的比例）
            ref_width, ref_height: 参考分辨率
            
        Returns:
            当前分辨率下的坐标
        """
        current_w, current_h = self.screen_size
        
        # 如果是 0-1 之间的比例
        if 0 <= x <= 1 and 0 <= y <= 1:
            return int(x * current_w), int(y * current_h)
        
        # 否则按比例缩放
        scale_x = current_w / ref_width
        scale_y = current_h / ref_height
        return int(x * scale_x), int(y * scale_y)
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None,
                       save_path: Optional[str] = None) -> np.ndarray:
        """
        截取屏幕
        
        Args:
            region: 截图区域 (left, top, width, height)
            save_path: 保存路径
            
        Returns:
            OpenCV 格式的图像数组
        """
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        if save_path:
            screenshot.save(save_path)
            
        # 转换为 OpenCV 格式 (BGR)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return img
    
    def find_text_location(self, text: str, 
                          region: Optional[Tuple[int, int, int, int]] = None,
                          lang: str = 'chi_sim+eng') -> Optional[Tuple[int, int]]:
        """
        使用 OCR 查找文字位置
        
        Args:
            text: 要查找的文字
            region: 搜索区域
            lang: Tesseract 语言（chi_sim=简体中文, eng=英文）
            
        Returns:
            文字中心坐标，未找到返回 None
        """
        try:
            # 截图
            screenshot = self.take_screenshot(region)
            
            # OCR 识别
            data = pytesseract.image_to_data(screenshot, lang=lang, output_type=pytesseract.Output.DICT)
            
            # 查找匹配文字
            for i, word in enumerate(data['text']):
                if text.lower() in word.lower():
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    
                    # 如果指定了区域，需要加上偏移
                    if region:
                        x += region[0]
                        y += region[1]
                    
                    if self.debug:
                        print(f"找到文字 '{text}' 在坐标 ({x}, {y})")
                    
                    return (x, y)
            
            return None
            
        except Exception as e:
            if self.debug:
                print(f"OCR 识别错误: {e}")
            return None
    
    def find_image_location(self, template_path: str,
                           region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        使用模板匹配查找图像位置
        
        Args:
            template_path: 模板图像路径
            region: 搜索区域
            
        Returns:
            图像中心坐标，未找到返回 None
        """
        try:
            # 读取模板
            template = cv2.imread(template_path)
            if template is None:
                if self.debug:
                    print(f"无法读取模板图像: {template_path}")
                return None
            
            # 截图
            screenshot = self.take_screenshot(region)
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.confidence:
                # 计算中心坐标
                h, w = template.shape[:2]
                x = max_loc[0] + w // 2
                y = max_loc[1] + h // 2
                
                # 如果指定了区域，需要加上偏移
                if region:
                    x += region[0]
                    y += region[1]
                
                if self.debug:
                    print(f"找到图像匹配，置信度 {max_val:.2f}，坐标 ({x}, {y})")
                
                return (x, y)
            
            if self.debug:
                print(f"未找到匹配（最高置信度 {max_val:.2f} < {self.confidence}）")
            
            return None
            
        except Exception as e:
            if self.debug:
                print(f"图像匹配错误: {e}")
            return None
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.0):
        """
        点击指定坐标
        
        Args:
            x, y: 坐标
            button: 按钮类型 ('left', 'right', 'middle')
            clicks: 点击次数
            interval: 点击间隔（秒）
        """
        pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
        if self.debug:
            print(f"点击坐标 ({x}, {y})，按钮={button}，次数={clicks}")
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """
        拖拽操作
        
        Args:
            start_x, start_y: 起始坐标
            end_x, end_y: 结束坐标
            duration: 拖拽持续时间（秒）
        """
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        if self.debug:
            print(f"拖拽从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
    
    def smart_click(self, target: str, 
                   method: str = 'auto',
                   region: Optional[Tuple[int, int, int, int]] = None,
                   **kwargs) -> bool:
        """
        智能点击 - 自动选择最佳方法定位目标
        
        Args:
            target: 目标（文字、图像路径或坐标）
            method: 定位方法 ('auto', 'text', 'image', 'coord')
            region: 搜索区域
            **kwargs: 传递给 click 的额外参数
            
        Returns:
            是否成功点击
        """
        location = None
        
        # 自动判断方法
        if method == 'auto':
            if Path(target).exists() and Path(target).suffix in ['.png', '.jpg', '.jpeg']:
                method = 'image'
            elif ',' in target or target.replace('.', '').replace('-', '').isdigit():
                method = 'coord'
            else:
                method = 'text'
        
        # 根据方法定位
        if method == 'text':
            location = self.find_text_location(target, region)
        elif method == 'image':
            location = self.find_image_location(target, region)
        elif method == 'coord':
            # 解析坐标
            if ',' in target:
                x, y = map(float, target.split(','))
            else:
                x, y = float(target), 0
            location = self.normalize_coordinates(x, y)
        
        # 执行点击
        if location:
            self.click(location[0], location[1], **kwargs)
            return True
        else:
            if self.debug:
                print(f"未能定位目标: {target}")
            return False
    
    def smart_drag(self, start_target: str, end_target: str,
                   method: str = 'auto',
                   region: Optional[Tuple[int, int, int, int]] = None,
                   duration: float = 0.5) -> bool:
        """
        智能拖拽 - 自动定位起点和终点
        
        Args:
            start_target: 起点目标
            end_target: 终点目标
            method: 定位方法
            region: 搜索区域
            duration: 拖拽持续时间
            
        Returns:
            是否成功拖拽
        """
        # 定位起点
        if method == 'auto':
            if Path(start_target).exists():
                start_loc = self.find_image_location(start_target, region)
            else:
                start_loc = self.find_text_location(start_target, region)
        elif method == 'text':
            start_loc = self.find_text_location(start_target, region)
        elif method == 'image':
            start_loc = self.find_image_location(start_target, region)
        else:
            x, y = map(float, start_target.split(','))
            start_loc = self.normalize_coordinates(x, y)
        
        # 定位终点
        if method == 'auto':
            if Path(end_target).exists():
                end_loc = self.find_image_location(end_target, region)
            else:
                end_loc = self.find_text_location(end_target, region)
        elif method == 'text':
            end_loc = self.find_text_location(end_target, region)
        elif method == 'image':
            end_loc = self.find_image_location(end_target, region)
        else:
            x, y = map(float, end_target.split(','))
            end_loc = self.normalize_coordinates(x, y)
        
        # 执行拖拽
        if start_loc and end_loc:
            self.drag(start_loc[0], start_loc[1], end_loc[0], end_loc[1], duration)
            return True
        else:
            if self.debug:
                print(f"未能定位起点或终点: {start_target} -> {end_target}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Windows 屏幕控制工具')
    parser.add_argument('action', choices=['click', 'drag', 'screenshot', 'find'],
                       help='操作类型')
    parser.add_argument('--target', help='目标（文字/图像路径/坐标）')
    parser.add_argument('--start', help='起点（用于拖拽）')
    parser.add_argument('--end', help='终点（用于拖拽）')
    parser.add_argument('--method', choices=['auto', 'text', 'image', 'coord'],
                       default='auto', help='定位方法')
    parser.add_argument('--region', help='搜索区域 (left,top,width,height)')
    parser.add_argument('--button', default='left', help='鼠标按钮')
    parser.add_argument('--clicks', type=int, default=1, help='点击次数')
    parser.add_argument('--duration', type=float, default=0.5, help='拖拽持续时间')
    parser.add_argument('--confidence', type=float, default=0.8, help='图像匹配置信度')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    # 解析区域
    region = None
    if args.region:
        region = tuple(map(int, args.region.split(',')))
    
    # 创建控制器
    controller = ScreenController(confidence=args.confidence, debug=args.debug)
    
    # 执行操作
    if args.action == 'click':
        if not args.target:
            print("错误：需要指定 --target")
            sys.exit(1)
        
        success = controller.smart_click(
            args.target,
            method=args.method,
            region=region,
            button=args.button,
            clicks=args.clicks
        )
        
        if success:
            print(json.dumps({"status": "success", "action": "click", "target": args.target}))
        else:
            print(json.dumps({"status": "failed", "action": "click", "target": args.target}))
            sys.exit(1)
    
    elif args.action == 'drag':
        if not args.start or not args.end:
            print("错误：需要指定 --start 和 --end")
            sys.exit(1)
        
        success = controller.smart_drag(
            args.start,
            args.end,
            method=args.method,
            region=region,
            duration=args.duration
        )
        
        if success:
            print(json.dumps({"status": "success", "action": "drag", "start": args.start, "end": args.end}))
        else:
            print(json.dumps({"status": "failed", "action": "drag", "start": args.start, "end": args.end}))
            sys.exit(1)
    
    elif args.action == 'screenshot':
        output = args.output or 'screenshot.png'
        controller.take_screenshot(region=region, save_path=output)
        print(json.dumps({"status": "success", "action": "screenshot", "path": output}))
    
    elif args.action == 'find':
        if not args.target:
            print("错误：需要指定 --target")
            sys.exit(1)
        
        if args.method == 'text' or (args.method == 'auto' and not Path(args.target).exists()):
            location = controller.find_text_location(args.target, region)
        else:
            location = controller.find_image_location(args.target, region)
        
        if location:
            print(json.dumps({"status": "success", "action": "find", "location": location}))
        else:
            print(json.dumps({"status": "failed", "action": "find", "target": args.target}))
            sys.exit(1)


if __name__ == '__main__':
    main()
