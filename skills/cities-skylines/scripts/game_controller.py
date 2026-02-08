#!/usr/bin/env python3
"""
Cities Skylines 游戏控制器 - 增强版
支持操作序列、智能验证、状态检测
"""

import sys
import json
import time
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Callable
import subprocess
from dataclasses import dataclass
from enum import Enum

# 依赖 screen-control
SCREEN_CONTROL = Path(__file__).parent.parent.parent / "screen-control" / "scripts" / "screen_controller.py"


class GameState(Enum):
    """游戏状态"""
    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    MENU_OPEN = "menu_open"


@dataclass
class OperationResult:
    """操作结果"""
    success: bool
    action: str
    message: str = ""
    data: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class GameController:
    """游戏控制器 - 智能操作与验证"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.current_state = GameState.UNKNOWN
        self.operation_history = []
        
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """加载配置"""
        default_config = {
            "automation": {
                "action_delay": 0.5,
                "verify_delay": 0.3,
                "max_retries": 3,
                "confidence_threshold": 0.85
            },
            "game": {
                "resolution": "3840x2160",
                "language": "chinese"
            }
        }
        
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _screen_cmd(self, action: str, **kwargs) -> Dict:
        """执行 screen-control 命令"""
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
            return {
                "status": "error", 
                "output": result.stdout, 
                "error": result.stderr
            }
    
    def _delay(self, delay_type: str = "action"):
        """统一延迟"""
        if delay_type == "action":
            time.sleep(self.config["automation"]["action_delay"])
        elif delay_type == "verify":
            time.sleep(self.config["automation"]["verify_delay"])
    
    # === 基础操作 ===
    
    def screenshot(self, output_path: str, region: Optional[str] = None) -> OperationResult:
        """截图"""
        result = self._screen_cmd("screenshot", output=output_path, region=region)
        
        if result.get("status") == "success":
            return OperationResult(
                success=True,
                action="screenshot",
                message=f"已保存到 {output_path}",
                data={"path": output_path}
            )
        else:
            return OperationResult(
                success=False,
                action="screenshot",
                message="截图失败"
            )
    
    def click(self, target: str, method: str = "auto", 
              button: str = "left", clicks: int = 1,
              verify: Optional[Callable] = None) -> OperationResult:
        """点击（带验证）"""
        max_retries = self.config["automation"]["max_retries"]
        
        for attempt in range(max_retries):
            # 执行点击
            result = self._screen_cmd("click", target=target, method=method,
                                     button=button, clicks=clicks)
            
            if result.get("status") != "success":
                continue
            
            self._delay("action")
            
            # 如果有验证函数，检查结果
            if verify:
                self._delay("verify")
                if verify():
                    return OperationResult(
                        success=True,
                        action="click",
                        message=f"点击 {target} 成功（已验证）",
                        data={"target": target, "attempts": attempt + 1}
                    )
            else:
                # 无验证，直接成功
                return OperationResult(
                    success=True,
                    action="click",
                    message=f"点击 {target} 成功",
                    data={"target": target}
                )
        
        return OperationResult(
            success=False,
            action="click",
            message=f"点击 {target} 失败（尝试 {max_retries} 次）"
        )
    
    def drag(self, start: str, end: str, duration: float = 0.5,
             verify: Optional[Callable] = None) -> OperationResult:
        """拖拽（带验证）"""
        result = self._screen_cmd("drag", start=start, end=end)
        
        if result.get("status") == "success":
            self._delay("action")
            
            if verify:
                self._delay("verify")
                if not verify():
                    return OperationResult(
                        success=False,
                        action="drag",
                        message="拖拽验证失败"
                    )
            
            return OperationResult(
                success=True,
                action="drag",
                message=f"拖拽 {start} -> {end} 成功",
                data={"start": start, "end": end}
            )
        
        return OperationResult(
            success=False,
            action="drag",
            message="拖拽失败"
        )
    
    # === 智能验证 ===
    
    def verify_ui_element(self, element: str, method: str = "auto",
                         timeout: float = 2.0) -> bool:
        """验证 UI 元素是否出现"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self._screen_cmd("click", target=element, method=method)
            
            # 只查找，不真的点击（通过检查是否能找到）
            # TODO: 需要 screen-control 支持 find-only 模式
            if result.get("status") == "success":
                return True
            
            time.sleep(0.2)
        
        return False
    
    def verify_screenshot_changed(self, before_path: str, after_path: str,
                                 threshold: float = 0.05) -> bool:
        """验证截图是否改变（简单像素差异检测）"""
        try:
            from PIL import Image
            import numpy as np
            
            img1 = Image.open(before_path).convert('RGB')
            img2 = Image.open(after_path).convert('RGB')
            
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            
            diff = np.mean(np.abs(arr1 - arr2)) / 255.0
            
            return diff > threshold
        except:
            return False
    
    # === 操作序列 ===
    
    def sequence(self, steps: List[Dict]) -> OperationResult:
        """执行操作序列
        
        示例:
        [
            {"action": "click", "target": "roads_icon"},
            {"action": "click", "target": "highway_tool"},
            {"action": "drag", "start": "0.3,0.4", "end": "0.7,0.6"},
            {"action": "wait", "duration": 1.0},
            {"action": "verify", "element": "road_built_indicator"}
        ]
        """
        results = []
        
        for i, step in enumerate(steps):
            action_type = step.get("action")
            
            if action_type == "click":
                result = self.click(
                    target=step["target"],
                    method=step.get("method", "auto"),
                    button=step.get("button", "left"),
                    clicks=step.get("clicks", 1)
                )
            
            elif action_type == "drag":
                result = self.drag(
                    start=step["start"],
                    end=step["end"]
                )
            
            elif action_type == "wait":
                time.sleep(step.get("duration", 1.0))
                result = OperationResult(
                    success=True,
                    action="wait",
                    message=f"等待 {step.get('duration', 1.0)}s"
                )
            
            elif action_type == "verify":
                success = self.verify_ui_element(step["element"])
                result = OperationResult(
                    success=success,
                    action="verify",
                    message=f"验证 {step['element']}: {'成功' if success else '失败'}"
                )
            
            elif action_type == "screenshot":
                result = self.screenshot(step["output"])
            
            else:
                result = OperationResult(
                    success=False,
                    action="unknown",
                    message=f"未知操作: {action_type}"
                )
            
            results.append(result)
            
            # 如果某一步失败且设置了 stop_on_failure
            if not result.success and step.get("stop_on_failure", True):
                return OperationResult(
                    success=False,
                    action="sequence",
                    message=f"序列在步骤 {i+1} 失败: {result.message}",
                    data={"completed_steps": i, "total_steps": len(steps), "results": results}
                )
        
        # 全部成功
        return OperationResult(
            success=True,
            action="sequence",
            message=f"序列执行成功（{len(steps)} 步）",
            data={"results": results}
        )
    
    # === 游戏专用高级操作 ===
    
    def build_road(self, road_type: str, start: Tuple[float, float], 
                   end: Tuple[float, float]) -> OperationResult:
        """建造道路（完整流程）"""
        steps = [
            {"action": "click", "target": "roads_icon", "method": "auto"},
            {"action": "wait", "duration": 0.3},
            {"action": "click", "target": f"{road_type}_tool", "method": "auto"},
            {"action": "wait", "duration": 0.3},
            {
                "action": "drag", 
                "start": f"{start[0]},{start[1]}", 
                "end": f"{end[0]},{end[1]}"
            }
        ]
        
        return self.sequence(steps)
    
    def zone_area(self, zone_type: str, corner1: Tuple[float, float],
                  corner2: Tuple[float, float]) -> OperationResult:
        """划分区域（完整流程）"""
        steps = [
            {"action": "click", "target": "zones_icon"},
            {"action": "wait", "duration": 0.3},
            {"action": "click", "target": f"{zone_type}_tool"},
            {"action": "wait", "duration": 0.3},
            {
                "action": "drag",
                "start": f"{corner1[0]},{corner1[1]}",
                "end": f"{corner2[0]},{corner2[1]}"
            }
        ]
        
        return self.sequence(steps)
    
    def place_building(self, building_type: str, 
                      location: Tuple[float, float]) -> OperationResult:
        """放置建筑（完整流程）"""
        steps = [
            {"action": "click", "target": "services_icon"},
            {"action": "wait", "duration": 0.3},
            {"action": "click", "target": f"{building_type}_icon"},
            {"action": "wait", "duration": 0.3},
            {"action": "click", "target": f"{location[0]},{location[1]}"}
        ]
        
        return self.sequence(steps)


# === 预定义操作模板 ===

class GamePatterns:
    """游戏模式 - 预定义的复杂操作"""
    
    @staticmethod
    def build_grid_roads(controller: GameController, 
                        origin: Tuple[float, float],
                        rows: int, cols: int,
                        spacing: float = 0.05) -> OperationResult:
        """建造网格道路"""
        print(f"建造网格道路: {rows}x{cols}, 起点 {origin}, 间距 {spacing}")
        
        ox, oy = origin
        
        # 横向道路
        for i in range(rows + 1):
            y = oy + i * spacing
            result = controller.build_road(
                "two_lane",
                (ox, y),
                (ox + cols * spacing, y)
            )
            if not result.success:
                return OperationResult(
                    success=False,
                    action="build_grid",
                    message=f"横向道路 {i} 失败: {result.message}"
                )
        
        # 纵向道路
        for j in range(cols + 1):
            x = ox + j * spacing
            result = controller.build_road(
                "two_lane",
                (x, oy),
                (x, oy + rows * spacing)
            )
            if not result.success:
                return OperationResult(
                    success=False,
                    action="build_grid",
                    message=f"纵向道路 {j} 失败: {result.message}"
                )
        
        return OperationResult(
            success=True,
            action="build_grid",
            message=f"网格道路建造完成: {rows}x{cols}"
        )


def main():
    """命令行测试入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cities Skylines 增强控制器')
    parser.add_argument('command', choices=[
        'test', 'screenshot', 'click', 'drag',
        'build_road', 'zone', 'place_building', 'grid'
    ])
    parser.add_argument('--target', help='目标')
    parser.add_argument('--start', help='起点 (x,y)')
    parser.add_argument('--end', help='终点 (x,y)')
    parser.add_argument('--type', help='类型')
    parser.add_argument('--output', help='输出路径')
    parser.add_argument('--rows', type=int, default=3)
    parser.add_argument('--cols', type=int, default=3)
    parser.add_argument('--spacing', type=float, default=0.05)
    
    args = parser.parse_args()
    
    controller = GameController()
    
    result = None
    
    if args.command == 'test':
        print("[OK] GameController 初始化成功")
        print(f"配置: {json.dumps(controller.config, indent=2, ensure_ascii=False)}")
        return 0
    
    elif args.command == 'screenshot':
        result = controller.screenshot(args.output or "test_screenshot.png")
        print(f"[{'OK' if result.success else 'FAIL'}] {result.message}")
    
    elif args.command == 'click':
        result = controller.click(args.target)
        print(f"[{'OK' if result.success else 'FAIL'}] {result.message}")
    
    elif args.command == 'drag':
        result = controller.drag(args.start, args.end)
        print(f"[{'OK' if result.success else 'FAIL'}] {result.message}")
    
    elif args.command == 'build_road':
        start = tuple(map(float, args.start.split(',')))
        end = tuple(map(float, args.end.split(',')))
        result = controller.build_road(args.type or "two_lane", start, end)
        print(f"[{'OK' if result.success else 'FAIL'}] {result.message}")
    
    elif args.command == 'grid':
        origin = tuple(map(float, args.start.split(',')))
        result = GamePatterns.build_grid_roads(
            controller, origin, args.rows, args.cols, args.spacing
        )
        print(f"[{'OK' if result.success else 'FAIL'}] {result.message}")
    
    return 0 if result.success else 1


if __name__ == '__main__':
    sys.exit(main())
