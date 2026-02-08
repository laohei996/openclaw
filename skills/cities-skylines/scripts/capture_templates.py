#!/usr/bin/env python3
"""
模板捕获工具 - 用于捕获游戏 UI 元素作为模板
"""

import sys
import time
from pathlib import Path
import pyautogui
from PIL import Image

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def capture_template(category: str, name: str, region: tuple = None):
    """
    捕获模板
    
    Args:
        category: 类别 (ui_elements, building_icons, etc.)
        name: 模板名称
        region: 截图区域 (left, top, width, height)，None 表示让用户选择
    """
    output_dir = TEMPLATES_DIR / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{name}.png"
    
    if region:
        # 直接截图指定区域
        screenshot = pyautogui.screenshot(region=region)
    else:
        # 交互式选择区域
        print(f"\n正在捕获: {category}/{name}")
        print("操作步骤:")
        print("1. 切换到游戏窗口")
        print("2. 将鼠标移动到目标元素的 **左上角**")
        print("3. 按 Enter 键确认左上角位置")
        
        input("按 Enter 继续...")
        
        time.sleep(0.5)
        left, top = pyautogui.position()
        print(f"左上角: ({left}, {top})")
        
        print("\n4. 将鼠标移动到目标元素的 **右下角**")
        print("5. 按 Enter 键确认右下角位置")
        
        input("按 Enter 继续...")
        
        time.sleep(0.5)
        right, bottom = pyautogui.position()
        print(f"右下角: ({right}, {bottom})")
        
        width = right - left
        height = bottom - top
        
        if width <= 0 or height <= 0:
            print("错误: 区域无效")
            return False
        
        # 截图
        region = (left, top, width, height)
        screenshot = pyautogui.screenshot(region=region)
    
    # 保存
    screenshot.save(output_path)
    print(f"✓ 已保存: {output_path}")
    print(f"  区域: {region}")
    
    # 显示预览（可选）
    try:
        screenshot.show()
    except:
        pass
    
    return True


def guided_capture():
    """引导式批量捕获"""
    print("=" * 50)
    print("Cities Skylines 模板捕获工具")
    print("=" * 50)
    
    print("\n推荐捕获的 UI 元素:")
    print("1. 底部菜单图标 (roads, zones, services, etc.)")
    print("2. 工具选项 (two_lane, four_lane, highway, etc.)")
    print("3. 分区类型 (residential_low, commercial, industrial, etc.)")
    print("4. 服务建筑图标 (school, hospital, police, fire, etc.)")
    
    templates = [
        # 底部菜单
        ("ui_elements", "roads_icon", "道路菜单"),
        ("ui_elements", "zones_icon", "分区菜单"),
        ("ui_elements", "services_icon", "服务菜单"),
        ("ui_elements", "beautification_icon", "美化菜单"),
        
        # 道路工具
        ("ui_elements", "two_lane_tool", "双车道道路"),
        ("ui_elements", "four_lane_tool", "四车道道路"),
        ("ui_elements", "highway_tool", "高速公路"),
        
        # 分区
        ("ui_elements", "residential_low_tool", "低密度住宅"),
        ("ui_elements", "residential_high_tool", "高密度住宅"),
        ("ui_elements", "commercial_low_tool", "低密度商业"),
        ("ui_elements", "commercial_high_tool", "高密度商业"),
        ("ui_elements", "industrial_tool", "工业区"),
        ("ui_elements", "office_tool", "办公区"),
        
        # 服务
        ("building_icons", "elementary_school", "小学"),
        ("building_icons", "high_school", "中学"),
        ("building_icons", "university", "大学"),
        ("building_icons", "clinic", "诊所"),
        ("building_icons", "hospital", "医院"),
        ("building_icons", "police_station", "警察局"),
        ("building_icons", "fire_station", "消防局"),
    ]
    
    print(f"\n共 {len(templates)} 个模板需要捕获")
    print("提示: 可以随时按 Ctrl+C 退出\n")
    
    input("准备好了吗? 按 Enter 开始...")
    
    for i, (category, name, description) in enumerate(templates, 1):
        print(f"\n[{i}/{len(templates)}] {description}")
        
        try:
            capture_template(category, name)
        except KeyboardInterrupt:
            print("\n\n已取消")
            break
        except Exception as e:
            print(f"错误: {e}")
            continue
        
        if i < len(templates):
            print("\n按 Enter 继续下一个，或 Ctrl+C 退出...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n\n已取消")
                break
    
    print("\n" + "=" * 50)
    print("捕获完成！")
    print(f"模板保存在: {TEMPLATES_DIR}")
    print("=" * 50)


def quick_capture():
    """快速单个捕获"""
    print("快速捕获模式")
    
    category = input("类别 (ui_elements/building_icons): ").strip()
    name = input("名称: ").strip()
    
    if not category or not name:
        print("错误: 类别和名称不能为空")
        return
    
    capture_template(category, name)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cities Skylines 模板捕获工具')
    parser.add_argument('--mode', choices=['guided', 'quick'], default='guided',
                       help='捕获模式')
    parser.add_argument('--category', help='类别')
    parser.add_argument('--name', help='名称')
    
    args = parser.parse_args()
    
    if args.mode == 'guided':
        guided_capture()
    elif args.mode == 'quick':
        if args.category and args.name:
            capture_template(args.category, args.name)
        else:
            quick_capture()


if __name__ == '__main__':
    main()
