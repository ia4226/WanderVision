import requests

# Replace with your Hugging Face API key
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"  # Ensure this model is available
headers = {"Authorization": "Bearer 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"}  # Replace *** with your actual API key


def query(payload):
    try:
        # Sending the request to Hugging Face API
        response = requests.post(API_URL, headers=headers, json=payload)

        # Check if the response is successful (status code 200)
        response.raise_for_status()  # Raises HTTPError if status code is not 200

        return response.json()  # Return the response as JSON
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None


# Sample input for the model
payload = {
    "inputs": "Can you please let us know more details about your "
}

# Get the output from the model
output = query(payload)

# If output is valid, print it
if output:
    print(output)
else:
    print("Error getting response from Hugging Face API.")
