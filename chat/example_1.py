import re
def get_response(user_input):
    if "store hours" in user_input.lower():
        return "Store hours are 9am-5pm, Monday to Sunday."
    elif "holiday" in user_input.lower():
        return "Store is closed on holidays, gazetted national holidays, and the third Saturday of the month."
    elif "delivery" in user_input.lower():
        return "Store has delivery service for orders worth a minimum of Rs. 500, or 10 or more different articles."
    elif re.search(r"(hello|hi|namaste)", user_input.lower()):
        return "Hello, how can I help you?"
    elif re.search(r"(bye|thank)", user_input.lower()):
        return "Goodbye!"
    elif "help" in user_input.lower():
        return "For HELP! contact: beststoreever.com, call: 9211921129, mail: bestbeststoreever@gmail.com"
    else:
        return "Sorry, I don't understand your query!"

def chat():
    print("Chatbot: Hi! I'm here to assist you. Type 'bye' to exit.")
    while True:
        user_input = input("You: ")
        response = get_response(user_input)
        print(f"Chatbot: {response}")

        # End the conversation if 'bye' is mentioned
        if "bye" in user_input.lower():
            break

if __name__ == "__main__":
    chat()
