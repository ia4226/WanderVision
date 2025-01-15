#dependencies
import re
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import requests
from geopy.geocoders import Nominatim
import random
#chatbot responses
class DementiaFriendlyChatbot:
    def __init__(self):
        self.responses = {
            r"(hello|hi|hey)": "Hello! How can I assist you today? I'm here to help.",
            r"(akshaya|srm|home)": "From Akshaya to SRM, you will need to ask for a public van, pay rupees 40 and distance will be approximately 8kms, with Akshaya being in Maraimalai Nagar and SRM in Potheri",
            r"(valliamai|Java)":"valliamai is a bus stop, Java is where everyone has food. Distance is 300meters and you have to return to TP, via clock tower route",
            r"(where am i|where is this)": "You are in WanderVision, a safe place where we assist you. How can I help you today?",
            r"(what day is it)": self.get_current_day,
            r"(help|assist|support)": "I can help with many things, such as taking your medication, guiding you, or just talking. What do you need help with?",
            r"(take|took) (medicine|medication)": "Time to take your medication is at 6:00 pm. Please follow your doctor’s instructions. Would you like help with that?",
            r"(time|what is the time)": self.get_current_time,
            r"(who are you|what are you)": "I am your helper, designed to support and guide you. If you need anything, I’m here.",
            r"(how are you|talking)": "I’m doing great, thank you for asking! How are you feeling today?",
            r"(thank you|thanks)": "You're very welcome! I'm happy to help. Let me know if you need anything else.",
            r"(exit|quit|goodbye)": "Goodbye! If you need help again, just ask. I’ll always be here to assist you.",
            r"(where is my family)": "Your family loves you very much, and they are thinking about you. They are at home and you can contact them with either you mobile phone or the WanderVision device",
            r"(what do i do next|guiding)": "Let’s take it easy. Would you like me to remind you of your tasks or just have a chat?",
            r"(who am i)": "You are a wonderful person, and I’m here to help you remember what’s important.",
            r"(tell me about my day)": "Today is a new day! You can take it one step at a time. What would you like to focus on today?",
            r"(work|home|rest)": self.get_lifestyle_responses,
            r"(do i need to sleep|when do i sleep)": "It’s important to rest and sleep well. Would you like me to remind you when it’s time to go to bed?",
            r"(what's in the room)": "You’re in a safe and comfortable space. The room has a few helpful items like your medication and a phone to reach out for assistance.",
            r"(distance|how far) from (.+?) to (.+)": self.get_distance_from_osm
        }

    def get_lifestyle_responses(self, user_input):
        #provide context-based responses
        if "work" in user_input:
            return "You work as a developer at XYZ. How is your work going today? Is there anything you need help with?"
        elif "home" in user_input:
            return "Your home is nearby, ask someone's help; it is in Dblock, Akshaya Metropolis, Maraimalai Nagar. How can I assist you there?"
        elif "rest" in user_input:
            return "Please take a deep breath, relax, and ask someone to help you contact your family. Would you like some rest right now?"
        else:
            return "I'm not sure how to respond to that. But whatever it is, you would be good at it"

    def get_current_time(self, user_input=None):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        return f"The current time is {current_time}. If you need help with anything else, feel free to ask."

    def get_current_day(self, user_input=None):
        now = datetime.now()
        current_day = now.strftime("%A")
        return f"Today is {current_day}. How can I assist you further?"

    def get_distance_from_osm(self, user_input):
        match = re.search(r"(distance|how far) from (.+?) to (.+)", user_input, re.IGNORECASE)
        if match:
            place1 = match.group(2)
            place2 = match.group(3)
            #Nominatim (Geopy)
            geolocator = Nominatim(user_agent="DementiaChatbot")
            location1 = geolocator.geocode(place1)
            location2 = geolocator.geocode(place2)

            print(f"Locations: {place1} -> {location1}, {place2} -> {location2}")
            #locations were successfully found
            if location1 and location2:
                #distance between coordinates using OSRM API
                distance = self.get_osrm_distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
                return f"The distance from {place1} to {place2} is approximately {distance} kilometers."
            else:
                return "I'm sorry, I couldn't find one or both locations. Please try again with more specific names (e.g., city names)."

        return "I couldn't understand the places you mentioned. Please try again with a more clear query."

    def get_osrm_distance(self, lat1, lon1, lat2, lon2):
        #OSRM API(needs work)
        osrm_url = f"http://router.project-osrm.org/table/v1/driving/{lon1},{lat1};{lon2},{lat2}?sources=0&destinations=1"
        try:
            response = requests.get(osrm_url)
            data = response.json()
            distance = data['rows'][0]['elements'][0]['distance'] / 1000  # convert meters to kilometers
            return round(distance, 2)
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return "Sorry, I couldn't calculate the distance right now."

    def get_response(self, user_input):
        #for pattern, response in self.responses.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                if callable(response):
                    return response(user_input)
                return response
            return "I’m not sure what you mean, but I’m here to help you however I can."

    def speak(self, text):
        #tts
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


def recognize_speech():
    #speech input from user.
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that. Can you please repeat?")
            return None
        except sr.RequestError:
            print("Sorry, I'm having trouble connecting to the speech service.")
            return None


def start_chat():
    bot = DementiaFriendlyChatbot()
    bot.speak("Hello! How can I assist you today? I am here to help you.")
    print("Dementia Chatbot: Hello! How can I assist you today? (Type 'exit' to quit)")

    while True:
        user_input = recognize_speech()

        if user_input == "exit":
            bot.speak("Goodbye! I’ll be here if you need help again.")
            print("Dementia Chatbot: Goodbye!")
            break
        if user_input:
            response = bot.get_response(user_input)
            print(f"Dementia Chatbot: {response}")
            bot.speak(response)

start_chat()
