import os
import tempfile
import pyttsx3
import whisper
import speech_recognition as sr
import string
from map_plotter import plot_route_on_map  # ✅ Importing map function
from weaviate_client import connect_to_weaviate, fetch_all_places


def recognize_speech():
    """Captures speech from the microphone and transcribes it using Whisper."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("📝 Transcribing...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio.get_wav_data())
            temp_audio_path = temp_audio.name

        model = whisper.load_model("base")
        result = model.transcribe(temp_audio_path)
        os.remove(temp_audio_path)

        transcript = result['text'].strip().lower()
        transcript = transcript.translate(str.maketrans('', '', string.punctuation))  # ✅ Remove punctuation
        print(f"✅ Recognized Speech: {transcript}")
        return transcript

    except Exception as e:
        print(f"❌ Error in speech recognition: {e}")
        return None


def speak_text(text):
    """Speak out text using pyttsx3."""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"❌ Error in text-to-speech: {e}")


def preprocess_numeric_input(user_input):
    """Convert spoken numbers into digits and remove punctuation."""
    word_to_number = {
        "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6",
        "seven": "7", "eight": "8", "nine": "9"
    }
    processed_input = user_input.lower().strip().translate(
        str.maketrans('', '', string.punctuation))  # ✅ Strip punctuation
    return word_to_number.get(processed_input, processed_input)


def choose_location(places, prompt):
    """Let the user choose a location from a list."""
    speak_text(prompt)

    for i, place in enumerate(places, start=1):
        speak_text(f"{i} for {place['name']}")

    while True:
        user_input = recognize_speech()
        if not user_input:
            speak_text("I couldn't understand you. Please try again.")
            continue

        processed_input = preprocess_numeric_input(user_input)
        print(f"DEBUG: User said '{user_input}', processed as '{processed_input}'")  # ✅ Debugging

        if processed_input.isdigit() and 1 <= int(processed_input) <= len(places):
            return places[int(processed_input) - 1]
        else:
            speak_text("Invalid input. Please try again.")


def navigation_menu(client):
    """Allow the user to select both start and end locations for navigation."""
    places = fetch_all_places(client)

    if len(places) < 2:
        speak_text("Not enough places found in the database for navigation.")
        return

    # ✅ Step 1: Choose Start Location
    start_location = choose_location(places, "Please choose your starting location by saying the number.")

    # ✅ Remove chosen start location from options
    remaining_places = [p for p in places if p != start_location]

    # ✅ Step 2: Choose Destination
    end_location = choose_location(remaining_places, "Please choose your destination by saying the number.")

    # ✅ Extract coordinates for navigation
    start_coords = (start_location["latitude"], start_location["longitude"])
    end_coords = (end_location["latitude"], end_location["longitude"])

    speak_text(f"Navigating from {start_location['name']} to {end_location['name']}. Directions will be displayed.")
    print(f"📍 Directions from {start_location['name']} → {end_location['name']}")

    # ✅ Plot route using imported function
    plot_route_on_map(route_coordinates=[], start_coords=start_coords, end_coords=end_coords)
    speak_text("Directions displayed successfully.")


def speech_command(client):
    """Handles speech-to-speech interaction with menu-driven voice commands."""
    while True:
        speak_text("Say one for navigation, two for safe points, three to exit.")

        user_input = recognize_speech()
        if not user_input:
            speak_text("I couldn't understand you. Please try again.")
            continue

        processed_input = preprocess_numeric_input(user_input)
        print(f"DEBUG: Main menu user input: '{user_input}', processed as '{processed_input}'")  # ✅ Debugging

        if processed_input == "1":
            navigation_menu(client)
        elif processed_input == "2":
            speak_text("Safe points feature is under development.")
        elif processed_input == "3" or processed_input in ["exit", "quit", "stop"]:
            speak_text("Exiting voice mode. Goodbye!")
            break
        else:
            speak_text("Invalid input. Please say a valid number.")


if __name__ == "__main__":
    weaviate_client = connect_to_weaviate()
    if weaviate_client:
        speech_command(weaviate_client)
