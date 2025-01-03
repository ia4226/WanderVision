import whisper

model = whisper.load_model("base")
result = model.transcribe(r"C:\Users\iarha\Dropbox\PC\Downloads\audio1.wav", fp16=False)
print(result["text"])


