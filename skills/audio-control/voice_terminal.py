import os
import sys
import subprocess
import time
import tempfile

# 强制 UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
MIC_NAME = "麦克风 (Realtek(R) Audio)"
TRANSCRIBE_SCRIPT = r"C:\Users\admin\Desktop\transcribe_wrapper.py"
AGENT_CMD = ["openclaw", "agent", "--deliver", "--channel", "webchat", "--to", "main"]

def record_fixed_duration(duration=5):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_name = tmp.name
    
    try:
        print(f"\r[录音中...] 剩 {duration} 秒", end="", flush=True)
        # 简单地分秒显示倒计时
        cmd = [
            "ffmpeg", "-y", "-loglevel", "quiet", "-f", "dshow", "-i", f"audio={MIC_NAME}",
            "-t", str(duration), "-ar", "16000", "-ac", "1", tmp_name
        ]
        subprocess.run(cmd)
        return tmp_name
    except Exception as e:
        print(f"\n录音失败: {e}")
        return None

def main():
    os.system("title 小黑语音终端 🖤")
    print("========================================")
    print("        小黑语音终端 (Xiǎo Hēi)         ")
    print("========================================")
    print(" 模式: 手动触发 (按回车开始/停止)        ")
    print(" 命令: '退出' 可结束程序                 ")
    print("----------------------------------------")

    while True:
        input("\n>>> 按 [回车] 开始 5 秒语音输入 (或输入 'q' 退出): ")
        
        tmp_wav = record_fixed_duration(5)
        if not tmp_wav: continue
        
        print("\n[识别中...]", end="", flush=True)
        result = subprocess.run(
            ["python", TRANSCRIBE_SCRIPT, tmp_wav],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        os.remove(tmp_wav)
        
        text = result.stdout.strip()
        if not text or len(text) < 1:
            print("\r[未检测到有效语音]           ")
            continue
            
        print(f"\r[你说了]: {text}")
        
        if "退出" in text or text.lower() == "q":
            print("再见！")
            break
            
        print("[发送给小黑...]", end="", flush=True)
        # 调用 openclaw agent 发送指令
        agent_proc = subprocess.run(
            AGENT_CMD + ["--message", text],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        print("\r[已发送]                     ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n退出语音终端。")
