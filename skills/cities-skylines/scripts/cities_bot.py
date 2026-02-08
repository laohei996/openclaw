#!/usr/bin/env python3
"""
Cities Skylines 游戏助手 - 核心自动化脚本
整合 screen-control，提供城市天际线专用的自动化功能
"""

import sys
import json
import time
from pathlib import Path
from typing import Tuple, Optional, List, Dict
import subprocess

# Screen control 路径
SCREEN_CONTROL = Path(__file__).parent.parent.parent / "screen-control" / "scripts" / "screen_controller.py"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


class CitiesSkylinesBot:
    """城市天际线游戏助手"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化助手"""
        self.config = self.load_config(config_path or CONFIG_FILE)
        self.templates = TEMPLATES_DIR
        
    def load_config(self, config_path: Path) -> Dict:
        """加载配置"""
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "game": {
                    "resolution": "3840x2160",
                    "language": "chinese",
                    "dlc": []
                },
                "automation": {
                    "speed": "normal",
                    "confidence": 0.85,
                    "pause_between_actions": 0.5
                },
                "learning": {
                    "record_screenshots": True,
                    "track_stats": True
                }
            }
    
    def save_config(self):
        """保存配置"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def screen_control(self, action: str, **kwargs) -> Dict:
        """调用 screen-control"""
        cmd = [sys.executable, str(SCREEN_CONTROL), action]
        
        # 添加参数
        for key, value in kwargs.items():
            if value is not None:
                cmd.append(f"--{key}")
                if value is not True:  # 布尔标志不需要值
                    cmd.append(str(value))
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 解析输出
        try:
            return json.loads(result.stdout)
        except:
            return {"status": "error", "output": result.stdout, "error": result.stderr}
    
    def find_ui_element(self, element_name: str, method: str = "auto") -> Optional[Tuple[int, int]]:
        """查找 UI 元素"""
        # 尝试模板匹配
        template_path = self.templates / "ui_elements" / f"{element_name}.png"
        if template_path.exists():
            result = self.screen_control("find", target=str(template_path), method="image")
            if result.get("status") == "success":
                return tuple(result["location"])
        
        # 尝试 OCR
        if method in ["auto", "text"]:
            result = self.screen_control("find", target=element_name, method="text")
            if result.get("status") == "success":
                return tuple(result["location"])
        
        return None
    
    def click_ui(self, element_name: str, **kwargs) -> bool:
        """点击 UI 元素"""
        # 尝试使用模板
        template_path = self.templates / "ui_elements" / f"{element_name}.png"
        if template_path.exists():
            result = self.screen_control("click", target=str(template_path), method="image", **kwargs)
        else:
            # 使用文字识别
            result = self.screen_control("click", target=element_name, method="auto", **kwargs)
        
        time.sleep(self.config["automation"]["pause_between_actions"])
        return result.get("status") == "success"
    
    def take_screenshot(self, name: str = "screenshot") -> str:
        """截图"""
        output = self.templates / "game_state" / f"{name}_{int(time.time())}.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        
        result = self.screen_control("screenshot", output=str(output))
        return str(output) if result.get("status") == "success" else None
    
    # === 游戏操作 ===
    
    def open_menu(self, menu_name: str) -> bool:
        """打开菜单（道路/分区/服务等）"""
        print(f"打开菜单: {menu_name}")
        return self.click_ui(f"{menu_name}_icon")
    
    def select_tool(self, tool_name: str) -> bool:
        """选择工具"""
        print(f"选择工具: {tool_name}")
        return self.click_ui(f"{tool_name}_tool")
    
    def build_straight_road(self, start: Tuple[float, float], 
                           end: Tuple[float, float],
                           road_type: str = "two_lane") -> bool:
        """建造直线道路"""
        print(f"建造道路: {road_type} from {start} to {end}")
        
        # 1. 打开道路菜单
        if not self.open_menu("roads"):
            return False
        
        # 2. 选择道路类型
        if not self.select_tool(road_type):
            return False
        
        # 3. 拖拽建造
        start_str = f"{start[0]},{start[1]}"
        end_str = f"{end[0]},{end[1]}"
        result = self.screen_control("drag", start=start_str, end=end_str, 
                                    method="coord", duration=0.8)
        
        time.sleep(self.config["automation"]["pause_between_actions"])
        return result.get("status") == "success"
    
    def zone_area(self, corner1: Tuple[float, float], 
                  corner2: Tuple[float, float],
                  zone_type: str = "residential_low") -> bool:
        """划分区域"""
        print(f"划分区域: {zone_type} from {corner1} to {corner2}")
        
        # 1. 打开分区菜单
        if not self.open_menu("zones"):
            return False
        
        # 2. 选择区域类型
        if not self.select_tool(zone_type):
            return False
        
        # 3. 拖拽划分
        start_str = f"{corner1[0]},{corner1[1]}"
        end_str = f"{corner2[0]},{corner2[1]}"
        result = self.screen_control("drag", start=start_str, end=end_str,
                                    method="coord", duration=0.5)
        
        time.sleep(self.config["automation"]["pause_between_actions"])
        return result.get("status") == "success"
    
    def place_building(self, building_type: str, 
                      location: Tuple[float, float]) -> bool:
        """放置建筑"""
        print(f"放置建筑: {building_type} at {location}")
        
        # 1. 打开服务菜单
        if not self.open_menu("services"):
            return False
        
        # 2. 选择建筑
        if not self.click_ui(f"{building_type}_icon"):
            return False
        
        # 3. 点击放置
        loc_str = f"{location[0]},{location[1]}"
        result = self.screen_control("click", target=loc_str, method="coord")
        
        time.sleep(self.config["automation"]["pause_between_actions"])
        return result.get("status") == "success"
    
    # === 高级自动化 ===
    
    def create_grid(self, origin: Tuple[float, float], 
                   rows: int, cols: int,
                   spacing: float = 0.05,
                   road_type: str = "two_lane") -> bool:
        """创建网格道路"""
        print(f"创建网格: {rows}x{cols} at {origin}, spacing={spacing}")
        
        ox, oy = origin
        
        # 横向道路
        for i in range(rows + 1):
            y = oy + i * spacing
            self.build_straight_road(
                (ox, y),
                (ox + cols * spacing, y),
                road_type
            )
        
        # 纵向道路
        for j in range(cols + 1):
            x = ox + j * spacing
            self.build_straight_road(
                (x, oy),
                (x, oy + rows * spacing),
                road_type
            )
        
        return True
    
    def auto_zone_grid(self, origin: Tuple[float, float],
                      rows: int, cols: int,
                      spacing: float = 0.05,
                      zone_type: str = "residential_low") -> bool:
        """自动在网格中划分区域"""
        print(f"自动划分网格: {zone_type}")
        
        ox, oy = origin
        cell_size = spacing * 0.8  # 留出道路空间
        
        for i in range(rows):
            for j in range(cols):
                x = ox + j * spacing + spacing * 0.1
                y = oy + i * spacing + spacing * 0.1
                
                self.zone_area(
                    (x, y),
                    (x + cell_size, y + cell_size),
                    zone_type
                )
        
        return True
    
    def read_stat(self, stat_name: str) -> Optional[str]:
        """读取游戏统计数据（使用 OCR）"""
        # 截图统计面板区域
        # 注意：需要根据实际游戏调整区域
        region_map = {
            "population": "100,50,200,80",
            "money": "300,50,400,80",
            "traffic": "500,50,600,80"
        }
        
        region = region_map.get(stat_name)
        if not region:
            return None
        
        # 使用 OCR 读取
        result = self.screen_control("screenshot", region=region, 
                                    output=f"temp_{stat_name}.png")
        
        # TODO: 添加 OCR 解析逻辑
        return None
    
    # === 学习系统 ===
    
    def start_learning_session(self, goal: str):
        """开始学习会话"""
        session = {
            "goal": goal,
            "start_time": time.time(),
            "actions": [],
            "screenshots": []
        }
        
        # 保存初始状态
        screenshot = self.take_screenshot("session_start")
        session["screenshots"].append(screenshot)
        
        # 保存会话
        session_file = Path(__file__).parent.parent / f"session_{int(time.time())}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        print(f"学习会话已开始: {goal}")
        print(f"会话文件: {session_file}")
        return str(session_file)
    
    def record_action(self, session_file: str, action: str, **params):
        """记录操作"""
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        session["actions"].append({
            "time": time.time(),
            "action": action,
            "params": params
        })
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
    
    def end_learning_session(self, session_file: str):
        """结束学习会话"""
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        # 保存最终状态
        screenshot = self.take_screenshot("session_end")
        session["screenshots"].append(screenshot)
        session["end_time"] = time.time()
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        print(f"学习会话已结束")
        print(f"总时长: {session['end_time'] - session['start_time']:.1f}s")
        print(f"操作数: {len(session['actions'])}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cities Skylines 游戏助手')
    parser.add_argument('command', choices=[
        'test', 'screenshot', 'find', 'click',
        'build_road', 'zone', 'place_building',
        'create_grid', 'auto_zone'
    ])
    parser.add_argument('--target', help='目标元素')
    parser.add_argument('--start', help='起点坐标 (x,y)')
    parser.add_argument('--end', help='终点坐标 (x,y)')
    parser.add_argument('--type', help='类型（道路/区域/建筑）')
    parser.add_argument('--rows', type=int, default=5)
    parser.add_argument('--cols', type=int, default=5)
    parser.add_argument('--spacing', type=float, default=0.05)
    
    args = parser.parse_args()
    
    bot = CitiesSkylinesBot()
    
    if args.command == 'test':
        print("Cities Skylines Bot 初始化成功！")
        print(f"配置: {json.dumps(bot.config, indent=2, ensure_ascii=False)}")
    
    elif args.command == 'screenshot':
        path = bot.take_screenshot(args.target or "manual")
        print(f"截图已保存: {path}")
    
    elif args.command == 'find':
        if not args.target:
            print("错误: 需要 --target")
            return 1
        loc = bot.find_ui_element(args.target)
        print(f"位置: {loc}")
    
    elif args.command == 'click':
        if not args.target:
            print("错误: 需要 --target")
            return 1
        success = bot.click_ui(args.target)
        print(f"点击: {'成功' if success else '失败'}")
    
    elif args.command == 'build_road':
        if not args.start or not args.end:
            print("错误: 需要 --start 和 --end")
            return 1
        start = tuple(map(float, args.start.split(',')))
        end = tuple(map(float, args.end.split(',')))
        road_type = args.type or "two_lane"
        success = bot.build_straight_road(start, end, road_type)
        print(f"建造道路: {'成功' if success else '失败'}")
    
    elif args.command == 'create_grid':
        if not args.start:
            print("错误: 需要 --start")
            return 1
        origin = tuple(map(float, args.start.split(',')))
        success = bot.create_grid(origin, args.rows, args.cols, 
                                 args.spacing, args.type or "two_lane")
        print(f"创建网格: {'成功' if success else '失败'}")


if __name__ == '__main__':
    sys.exit(main() or 0)
