import os
import sys
import subprocess
import time
import tempfile
import traceback

# 强制 UTF-8 环境
def setup_encoding():
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

setup_encoding()

# 配置
MIC_NAME = "麦克风 (Realtek(R) Audio)"
TRANSCRIBE_SCRIPT = r"C:\Users\admin\Desktop\transcribe_wrapper.py"
AGENT_CMD = ["openclaw", "agent", "--deliver", "--channel", "webchat", "--to", "main"]
LOG_FILE = r"C:\Users\admin\Desktop\audio_debug.log"

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

def run_command(cmd, input_text=None):
    """鲁棒的命令运行函数"""
    try:
        # 尝试 UTF-8
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return res.stdout.strip()
    except Exception as e:
        log(f"Command execution error: {e}")
        return ""

def record_fixed_duration(duration=5):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name
    
    try:
        log(f"Recording for {duration} seconds...")
        # 录制
        cmd = [
            "ffmpeg", "-y", "-loglevel", "quiet", "-f", "dshow", "-i", f"audio={MIC_NAME}",
            "-t", str(duration), "-ar", "16000", "-ac", "1", tmp_name
        ]
        subprocess.run(cmd, capture_output=True)
        return tmp_name
    except Exception as e:
        log(f"Recording failed: {e}")
        return None

def main():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    os.system("title 小黑语音终端-调试版 🖤")
    log("=== 语音终端启动成功 ===")
    
    while True:
        print("\n" + "="*40)
        print(" >>> 按 [回车键] 开始录音 5 秒")
        print(" >>> 输入 'q' 退出")
        user_input = input(" > ")
        
        if user_input.lower() == 'q':
            break
            
        wav_file = record_fixed_duration(5)
        if not wav_file:
            continue
            
        log("Transcribing...")
        text = run_command(["python", TRANSCRIBE_SCRIPT, wav_file])
        if os.path.exists(wav_file):
            os.remove(wav_file)
            
        if not text:
            log("Result: [Empty]")
            continue
            
        log(f"Recognized: {text}")
        
        log("Sending to OpenClaw...")
        # 发送指令给 agent
        send_res = run_command(AGENT_CMD + ["--message", text])
        log(f"Agent response length: {len(send_res)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"FATAL ERROR: {traceback.format_exc()}\n")
        print(f"程序崩溃，请查看桌面上的 audio_debug.log")
        input("按回车键关闭...")
