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

# 配置 - 显式路径
MIC_NAME = "麦克风 (Realtek(R) Audio)"
TRANSCRIBE_SCRIPT = r"C:\Users\admin\Desktop\transcribe_wrapper.py"
OPENCLAW_PATH = r"C:\Users\admin\AppData\Roaming\npm\openclaw.cmd"
AGENT_CMD = [OPENCLAW_PATH, "agent", "--deliver", "--channel", "webchat", "--to", "main"]
LOG_FILE = r"C:\Users\admin\Desktop\audio_debug.log"

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except:
        pass

def run_command(cmd, env=None):
    """鲁棒的命令运行函数"""
    try:
        current_env = os.environ.copy()
        if env:
            current_env.update(env)
        
        # 强制 Python 和其他工具输出 UTF-8
        current_env["PYTHONIOENCODING"] = "utf-8"
        
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True, env=current_env)
        if res.returncode != 0 and res.stderr:
            log(f"Error Output: {res.stderr.strip()}")
        return res.stdout.strip()
    except Exception as e:
        log(f"Command execution error: {e}")
        return ""

def record_fixed_duration(duration=5):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name
    
    try:
        log(f"Recording for {duration} seconds...")
        cmd = [
            "ffmpeg", "-y", "-loglevel", "quiet", "-f", "dshow", "-i", f"audio={MIC_NAME}",
            "-t", str(duration), "-ar", "16000", "-ac", "1", tmp_name
        ]
        subprocess.run(cmd, capture_output=True, shell=True)
        return tmp_name
    except Exception as e:
        log(f"Recording failed: {e}")
        return None

def main():
    log("=== 语音终端启动成功 (V4 编码修复版) ===")
    
    while True:
        print("\n" + "="*40)
        print(" >>> 按 [回车键] 开始录音 5 秒")
        print(" >>> 输入 'q' 退出")
        try:
            user_input = input(" > ")
        except EOFError:
            break
        
        if user_input.lower() == 'q':
            break
            
        wav_file = record_fixed_duration(5)
        if not wav_file:
            continue
            
        log("Transcribing...")
        # 显式传递 UTF-8 编码环境变量
        text = run_command(["python", TRANSCRIBE_SCRIPT, wav_file])
        
        if os.path.exists(wav_file):
            try: os.remove(wav_file)
            except: pass
            
        if not text:
            log("Result: [Empty]")
            continue
            
        log(f"Recognized: {text}")
        
        log("Sending to OpenClaw...")
        # 发送指令给 agent
        send_res = run_command(AGENT_CMD + ["--message", f'"{text}"'])
        log(f"Agent response received (len: {len(send_res)})")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"FATAL ERROR: {traceback.format_exc()}\n")
        print(f"程序崩溃，请查看桌面上的 audio_debug.log")
        input("按回车键关闭...")
