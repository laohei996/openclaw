import os
import sys
import subprocess
import time
import tempfile
import numpy as np

# 强制 UTF-8 输出
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
MIC_NAME = "麦克风 (Realtek(R) Audio)"
TRANSCRIBE_SCRIPT = r"C:\Users\admin\Desktop\transcribe_wrapper.py"
ENERGY_THRESHOLD = 500  # 能量阈值，根据环境调整
SILENCE_DURATION = 1.5  # 静止超过 X 秒停止录音

def get_rms(audio_data):
    """计算音频块的 RMS (均方根) 作为能量指标"""
    return np.sqrt(np.mean(np.square(audio_data)))

def listen_and_transcribe():
    """监听麦克风，检测到说话并停止后进行转录"""
    print("Listening... (Press Ctrl+C to stop)")
    
    while True:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_name = tmp.name
        
        try:
            # 使用 ffmpeg 持续检测并录制
            # 这里的策略是：先通过 ffmpeg 录制一个小片段判断是否有声音
            # 或者使用 ffmpeg 的 silencedetect 过滤器 (稍微复杂点)
            
            # 为了演示简单，我们先实现一个“按需录制”：监听 2 秒，如果没声音就循环，有声音就继续录制直到安静
            # 实际上最稳妥的方式是使用 PyAudio，但目前环境里没有，我们尝试用 ffmpeg 实现简易 VAD
            
            print(".", end="", flush=True)
            record_cmd = [
                "ffmpeg", "-y", "-f", "dshow", "-i", f"audio={MIC_NAME}",
                "-t", "3", "-ar", "16000", "-ac", "1", tmp_name
            ]
            subprocess.run(record_cmd, capture_output=True, text=False)
            
            # 转录
            result = subprocess.run(
                ["python", TRANSCRIBE_SCRIPT, tmp_name],
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            
            text = result.stdout.strip()
            if text and len(text) > 1: # 过滤掉可能的噪音识别
                print(f"\nCaptured: {text}")
                # 这里可以触发后续逻辑
                return text
                
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        
        time.sleep(0.1)

if __name__ == "__main__":
    listen_and_transcribe()
