import os
import sys
import subprocess
import argparse

# 这是一个内部工具脚本，供 OpenClaw 代理调用
# 路径: C:\Users\admin\openclaw\skills\audio-control\audio_manager.py

VBS_PATH = r"C:\Users\admin\Desktop\play_voice.vbs"

def stop_playback():
    """停止播放 (杀掉 cscript 进程)"""
    subprocess.run(["taskkill", "/F", "/IM", "cscript.exe"], stderr=subprocess.DEVNULL)

def play_file(file_path):
    """播放文件"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return
    
    abs_path = os.path.abspath(file_path)
    
    # 停止之前的播放
    stop_playback()
    
    # 写入 VBS
    vbs_content = f'''Set Player = CreateObject("WMPlayer.OCX")
Player.URL = "{abs_path}"
Player.Controls.Play
Do While Player.playState <> 1
    WScript.Sleep 100
Loop
'''
    with open(VBS_PATH, "w", encoding="utf-8") as f:
        f.write(vbs_content)
    
    # 后台运行 VBS
    subprocess.Popen(["cscript", "//nologo", VBS_PATH], shell=True)
    print(f"Playing: {abs_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["play", "stop"], required=True)
    parser.add_argument("--file", help="Path to audio file")
    
    args = parser.parse_args()
    
    if args.action == "play" and args.file:
        play_file(args.file)
    elif args.action == "stop":
        stop_playback()
        print("Playback stopped.")
