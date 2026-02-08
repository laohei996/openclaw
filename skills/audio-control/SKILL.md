# audio-control Skill

音频播放与控制。

## Description

提供本地音频播放功能，支持直接播放音频文件或将文本转换为语音并播放。

## Tools

### audio_play

播放指定路径的音频文件或将文本转换为语音后播放。

- **file_path** (string, optional): 音频文件的绝对路径。
- **text** (string, optional): 要转换为语音并播放的文本。

### audio_stop

停止当前正在播放的所有音频。

### voice_terminal

启动一个独立的控制台窗口进行语音交互。

- **脚本路径**: `C:\Users\admin\openclaw\skills\audio-control\voice_terminal.py`
- **启动方式**: 运行桌面上的 `启动小黑语音终端.bat`。

## Implementation

使用 ffmpeg 录制，Whisper 转录，并通过 `openclaw agent` CLI 与当前会话同步。
