#ai.py

import os
import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API key
genai.configure(api_key = GOOGLE_API_KEY)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 500000,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


# Function to process chunks
def process_chunks(scraped_data, chunk_size=1000000):
    """Breaks scraped data into smaller chunks"""
    chunks = [scraped_data[i:i + chunk_size] for i in range(0, len(scraped_data), chunk_size)]
    return chunks

# Updated prompt with custom instructions
ex = str({'name':['tesla','honda','audi'],'price':[1,2,3]})
custom_prompt = """
You are tasked with extracting specific information from the following text content: {chunk}.
and your extraction must be 100 percentage accurate.
Please follow these instructions carefully:

1. **Extract Information:**you must~ Only extract the information that directly matches the provided description: {user_query}.
2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response.
3. **Empty Response:** If no information matches the description, return an empty string ('').
4. **Direct Data Only:** Your output should be a Python dictionary, where keys represent column headers and values are lists of data.
5. **Output Format:** You are required to provide your output strictly in the following format and adhere to these instructions without exception:
    5.1. **Raw Text Only:** Your output must be in raw text form how two people chat with each others without any tags, comments, explanations, or formatting. Do not use any markers like python, json,text or other code-related tags.
    5.2. **Output Example:** Your output should look exactly like this example:{ex}
    5.3. **No Deviations:** Do not include any additional text, symbols, or formatting, even if you think it might be helpful.
    5.4. **Context Awareness:** Understand that your response will be programmatically processed into a DataFrame. If your output does not exactly match the example format, it will cause errors.
    5.5. **Replace Null value:** if any null value in your out put replace with empty string.
6. **verification:** you must verify your output with {chunk} before giving replay. if it match 100 percentage give your replay else if its not 100 percentage accurate do your work from scratch until get 100 percentage accuracy. 
7.Responsibility: Any deviation from this format will result in the response being unusable. Ensure every response follows the example format provided above.
"""

# Function to convert AI response (Python dict) to DataFrame
def convert_ai_response_to_df(ai_response):
    try:
        if ai_response.startswith("```text") and ai_response.endswith("```"):
            cleaned_response = ai_response[7:-3].strip()
        elif ai_response.startswith("```") and ai_response.endswith("```"):
            cleaned_response = ai_response[3:-3].strip()
        elif ai_response.startswith('"""') and ai_response.endswith('"""'):
            cleaned_response = ai_response[3:-3].strip()
        elif ai_response.startswith("'''") and ai_response.endswith("'''"):
            cleaned_response = ai_response[3:-3].strip()
        elif ai_response.startswith("```json") and ai_response.endswith("```"):
            cleaned_response = ai_response[7:-3].strip()
        elif ai_response.startswith("```python") and ai_response.endswith("```"):
            cleaned_response = ai_response[9:-3].strip()
        else:
            cleaned_response = ai_response.strip()
        # Convert the string response to a Python dictionary
        response_dict = eval(cleaned_response.strip())
        max_length = max(len(v) for v in response_dict.values())
        # Normalize each list to the maximum length
        normalized_data = {k: v + [''] * (max_length - len(v)) for k, v in response_dict.items()}
        # Create DataFrame
        if not isinstance(normalized_data, dict):
            raise ValueError("AI response is not a valid Python dictionary.")
        # Convert dictionary to DataFrame
        df = pd.DataFrame(normalized_data)
        return df
    except Exception as e:
        raise ValueError(f"Error converting AI response to DataFrame: {e}")

# Modify the chunk processing and interaction with AI
def interact_with_ai(scraped_data, user_query):
    try:
        # Start chat session with empty history
        chat_session = model.start_chat(history=[])

        # Break scraped data into chunks if too large
        chunks = process_chunks(scraped_data)

        full_response = ""
        for chunk in chunks:
            # Format the prompt with chunk of scraped data and user query using the updated prompt
            prompt = custom_prompt.format(chunk=chunk, user_query=user_query, ex = ex)

            # Send message to Gemini AI for each chunk
            response = chat_session.send_message(prompt)
            full_response += response.text.strip() + "\n"    

        # Ensure no trailing newlines or extra whitespace
        full_response = full_response.strip()
        return full_response

    except Exception as e:
        return f"Error: {str(e)}", None, None