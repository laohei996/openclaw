import os
import sys
import subprocess
import time
import tempfile
import traceback
import winsound
import msvcrt

# Force UTF-8 environment
def setup_encoding():
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

setup_encoding()

# Config
MIC_ID = r"audio=@device_cm_{33D9A762-90C8-11D0-BD43-00A0C911CE86}\wave_{12A2538C-8A64-4AFF-8FE6-6017F42F9CAA}"
OPENCLAW_PATH = r"C:\Users\admin\AppData\Roaming\npm\openclaw.cmd"
TRANSCRIBE_SCRIPT = r"C:\Users\admin\Desktop\transcribe_wrapper.py"
LOG_FILE = r"C:\Users\admin\Desktop\audio_debug.log"
WAKE_WORD = "小黑"

QUICK_ACTIONS = {
    "1": "帮我看看现在的游戏状态",
    "2": "规划一条从市中心到工业区的路",
    "3": "清理一下桌面上的截图文件",
    "4": "讲个笑话"
}

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(f"\n{full_msg}")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except:
        pass

def play_beep(freq=1200, dur=100):
    try: winsound.Beep(freq, dur)
    except: pass

def update_status(status_text):
    sys.stdout.write(f"\r[状态]: {status_text:<60}")
    sys.stdout.flush()

def record(duration):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name
    try:
        cmd = [
            "ffmpeg", "-y", "-loglevel", "quiet", "-f", "dshow", "-i", MIC_ID,
            "-t", str(duration), "-ar", "16000", "-ac", "1", tmp_name
        ]
        subprocess.run(cmd, capture_output=True)
        return tmp_name
    except:
        return None

def transcribe(wav_path):
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        res = subprocess.run(["python", TRANSCRIBE_SCRIPT, wav_path], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        return res.stdout.strip()
    except:
        return ""

def send_to_agent_async(text):
    """Asynchronously send command to agent using a MORE robust method without shell nesting"""
    log(f"正在发送指令: {text}")
    update_status(f"发送中: {text}...")
    play_beep(1200, 80)
    
    # Explicitly targeting the session key found in openclaw sessions
    # Use session key instead of implicit logic to avoid parser errors
    cmd = [OPENCLAW_PATH, "agent", "--session-id", "3b4eb467-3fac-4660-8b53-9b9722d4dd10", "--message", text]
    
    try:
        # Avoid shell=True to bypass cmd.exe parsing quirks
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        update_status(f"✅ 指令已投递: {text}")
        play_beep(1500, 100)
    except Exception as e:
        log(f"投递失败: {e}")
        # Fallback to shell if absolute path fails without it
        try:
            subprocess.Popen(" ".join([f'"{c}"' for c in cmd]), shell=True)
            update_status("✅ (兼容模式) 指令已投递")
        except:
            update_status("❌ 指令投递失败")

def main():
    os.system("cls")
    print("====================================================")
    print("        小黑语音助手 V15 (Session 锁定版)          ")
    print("====================================================")
    print(" [快捷操作菜单]:")
    for k, v in QUICK_ACTIONS.items():
        print(f"   {k} -> {v}")
    print("-" * 50)
    print(f" [语音唤醒]: 喊 '{WAKE_WORD}'")
    print(" [退出程序]: 输入 'q'")
    print("====================================================")
    
    play_beep(1000, 100)
    
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            try: key = ch.decode('utf-8', errors='ignore')
            except: key = ""
                
            if key in QUICK_ACTIONS:
                send_to_agent_async(QUICK_ACTIONS[key])
                time.sleep(0.5) 
                continue
            elif key.lower() == 'q':
                break
        
        update_status(f"正在监听 '{WAKE_WORD}'...")
        
        tmp_wav = record(1.2)
        text = transcribe(tmp_wav)
        if os.path.exists(tmp_wav): os.remove(tmp_wav)
        
        if text:
            if WAKE_WORD in text:
                log(f"唤醒成功")
                play_beep(1800, 150)
                update_status("🎤 请说话，录音 6 秒...")
                
                cmd_wav = record(6)
                cmd_text = transcribe(cmd_wav)
                if os.path.exists(cmd_wav): os.remove(cmd_wav)
                
                if cmd_text:
                    print(f"\n" + "-"*40)
                    print(f" 识别内容: 「 {cmd_text} 」")
                    print(f" 确认发送? [Enter]发送 / [Esc]取消")
                    print("-"*40)
                    
                    while True:
                        if msvcrt.kbhit():
                            c = msvcrt.getch()
                            if c == b'\r':
                                send_to_agent_async(cmd_text)
                                break
                            elif c == b'\x1b':
                                update_status("已取消")
                                play_beep(600, 100)
                                break
                        time.sleep(0.05)
                else:
                    update_status("未识别到指令")
                    play_beep(400, 200)

        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL ERROR: {traceback.format_exc()}")
        input("Press Enter to exit...")
