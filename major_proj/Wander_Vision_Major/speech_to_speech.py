import speech_recognition as sr
import pyttsx3
import whisper
import tempfile
import os

def recognize_speech():
    """Captures speech from the microphone and transcribes it using Whisper."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # reduce background noise
        audio = recognizer.listen(source)

    try:
        print("Transcribing...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:#save file in WAV
            temp_audio.write(audio.get_wav_data())
            temp_audio_path = temp_audio.name

        # Load Whisper model
        model = whisper.load_model("base")
        result = model.transcribe(temp_audio_path)

        os.remove(temp_audio_path)

        transcript = result['text'].strip()
        return transcript.lower() if transcript else None
    except Exception as e:
        print("Error in speech recognition:", e)
        return None

def speech_command(client, query_weaviate):
    while True:
        user_input = recognize_speech()

        if user_input:
            print("Recognized:", user_input)

            if user_input in ["exit", "quit", "stop"]:  # Exit condition
                print("Exiting voice mode...")
                break

            answer = query_weaviate(client, user_input)
            print("Answer:", answer)

            engine = pyttsx3.init()
            engine.say(answer)
            engine.runAndWait()
        else:
            print("Couldn't understand. Try again.")
