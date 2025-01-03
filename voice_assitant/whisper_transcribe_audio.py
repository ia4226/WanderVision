import os

# Add FFmpeg's directory to the PATH at runtime
ffmpeg_path = r"C:\Users\iarha\Dropbox\PC\Downloads\ffmpeg\ffmpeg-7.1-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

import whisper

# Load model and run transcription
model = whisper.load_model("small")
result = model.transcribe(r"C:\Users\iarha\Dropbox\PC\Downloads\audio1.wav", fp16=False)
print(result["text"])