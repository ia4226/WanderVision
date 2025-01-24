from transformers import T5Tokenizer, T5ForConditionalGeneration
import weaviate
from weaviate.auth import AuthClientPassword
import re

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")

def connect_to_weaviate():
    url = "https://belhthdprsuurfecdtjqa.c0.asia-southeast1.gcp.weaviate.cloud"
    auth = AuthClientPassword(
        username="iarhatia@gmail.com",
        password="Shrikrishna#12",
    )
    return weaviate.Client(url=url, auth_client_secret=auth)

def preprocess_query(query):
    query = query.lower().strip()
    query = re.sub(r"[^\w\s]", "", query)
    query = re.sub(r"\s+", " ", query)

    keywords_to_ignore = ["what", "is", "where", "describe", "about", "the", "a"]
    words = query.split()
    filtered_words = [word for word in words if word not in keywords_to_ignore]
    return " ".join(filtered_words)
#query
def query_weaviate(client, query_class, filters, fields, additional_fields=None):
    query = client.query.get(query_class, fields)
    if filters:
        query = query.with_where(filters)
    if additional_fields:
        query = query.with_additional(additional_fields)
    results = query.do()
    #debugging
    print("DEBUG: Filters used:", filters)
    print("DEBUG: Fields requested:", fields)
    print("DEBUG: Query Results:", results)

    return results.get("data", {}).get("Get", {}).get(query_class, [])

def handle_special_queries(query):

    main_term = preprocess_query(query)  #main term of the query
    if any(word in query for word in ["where", "location", "coordinates", "longitude", "latitude", "position"]):
        #location-related data
        return {
            "operator": "Like",
            "path": ["name"],
            "valueString": f"*{main_term}*"
        }, ["name", "latitude", "longitude"]
    elif any(word in query for word in ["describe", "about", "what is", "details"]):
        #queries, fetch name and description
        return {
            "operator": "Like",
            "path": ["name"],
            "valueString": f"*{main_term}*"
        }, ["name", "description"]
    elif any(word in query for word in ["navigate", "route", "direction"]):
        #navigation-related queries, fetch location details
        return {
            "operator": "Like",
            "path": ["name"],
            "valueString": f"*{main_term}*"
        }, ["name", "latitude", "longitude", "description"]
    else:
        #filter for general queries
        return {
            "operator": "Like",
            "path": ["name"],
            "valueString": f"*{main_term}*"
        }, ["name", "description", "latitude", "longitude"]
#response using T5
def generate_response(prompts, batch_size=2):
    all_responses = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        input_ids = tokenizer(batch, return_tensors="pt", padding=True, truncation=True).input_ids
        outputs = model.generate(
            input_ids,
            max_length=500,
            num_beams=5,
            temperature=0.7,
            early_stopping=True,
            do_sample=True
        )
        responses = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        all_responses.extend(responses)
    return all_responses

#extract and format context from Weaviate results
def format_context(weaviate_results, query_type):

    if not weaviate_results:
        return "No relevant context available in the database."  # Robust handling for empty results

    if query_type in ["location", "coordinates"]:
        context = "\n".join([
            f"{result.get('name', 'Unknown')} - Coordinates: Latitude: {result.get('latitude', 'Unknown')}, Longitude: {result.get('longitude', 'Unknown')}"
            for result in weaviate_results
        ])
    elif query_type in ["description", "about", "what is", "details"]:
        context = "\n".join([
            f"{result.get('name', 'Unknown')} - Description: {result.get('description', 'No description available')}"
            for result in weaviate_results
        ])
    elif query_type in ["navigate", "route", "direction"]:
        context = "\n".join([
            f"{result.get('name', 'Unknown')} - Navigation Info:\n"
            f"Latitude: {result.get('latitude', 'Unknown')}, Longitude: {result.get('longitude', 'Unknown')}\n"
            f"Description: {result.get('description', 'No additional info available')}"
            for result in weaviate_results
        ])
    else:
        # Default general context
        context = "\n".join([
            f"{result.get('name', 'Unknown')} - Coordinates: Latitude: {result.get('latitude', 'Unknown')}, Longitude: {result.get('longitude', 'Unknown')}\n"
            f"Description: {result.get('description', 'No description available')}"
            for result in weaviate_results
        ])
    return context

# main interactive function
def main():
    client = connect_to_weaviate()
    print("\n--- Welcome to the WanderVision Chat System ---")
    print("You can ask about places, landmarks, or general information about stored entries.")

    try:
        while True:
            user_query = input("Enter your query or type 'exit' to quit: ").strip()
            if user_query.lower() == "exit":
                print("Goodbye!")
                break

            preprocessed_query = preprocess_query(user_query)
            query_type = (
                "location" if any(
                    word in preprocessed_query for word in
                    ["where", "coordinates", "longitude", "latitude", "position"]) else
                "description" if any(
                    word in preprocessed_query for word in ["describe", "about", "what is", "details"]) else
                "navigation" if any(word in preprocessed_query for word in ["navigate", "route", "direction"]) else
                "general"
            )

            filters, fields = handle_special_queries(preprocessed_query)

            weaviate_results = query_weaviate(client, "Place", filters, fields)

            if weaviate_results:
                context = format_context(weaviate_results, query_type)
                print(f"Found context:\n{context}")
            else:
                context = "No relevant data found in the database."
                print("No context found.")

            prompt = f"Context: {context}\nUser Query: {user_query}\nResponse:"
            response = generate_response([prompt])[0]
            print(f"AI Response: {response}")

    finally:
        client.close()

if __name__ == "__main__":
    main()
