import os
import sys
import subprocess
import time
import tempfile
from audio_manager import stop_playback

# 强制输出为 UTF-8，避免 Windows 控制台编码问题
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
MIC_NAME = "麦克风 (Realtek(R) Audio)"
TRANSCRIBE_SCRIPT = r"C:\Users\admin\Desktop\transcribe_wrapper.py"

def record_and_transcribe(duration=5):
    """录制并转录"""
    # 停止正在播放的音频，避免回声
    stop_playback()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name
    
    try:
        # 1. 录制音频
        # 使用 ffmpeg 录制指定时长
        record_cmd = [
            "ffmpeg", "-y", "-f", "dshow", "-i", f"audio={MIC_NAME}",
            "-t", str(duration), "-ar", "16000", "-ac", "1", tmp_name
        ]
        # 运行录制，忽略控制台输出
        subprocess.run(record_cmd, capture_output=True, text=False)
        
        # 2. 调用转录脚本
        # 调用时强制使用 utf-8 捕获
        result = subprocess.run(
            ["python", TRANSCRIBE_SCRIPT, tmp_name],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        
        if result.stdout:
            return result.stdout.strip()
        return None
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=5)
    args = parser.parse_args()
    
    text = record_and_transcribe(args.duration)
    if text:
        # 使用 print 触发刚才设置的 UTF-8 输出
        print(f"TRANSCRIPT_START\n{text}\nTRANSCRIPT_END")
    else:
        print("No speech detected.")
