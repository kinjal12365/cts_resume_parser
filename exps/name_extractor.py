import requests

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyDQXzyJl0V8VRJkk0H956lIFfLo_s4OPh4"
MODEL_NAME = "gemini-1.5-flash"
# ----------------------

def get_name_via_requests(resume_text: str, api_key: str) -> str:
    """
    Extracts a person's name from text using the Gemini REST API.
    """
    if not resume_text:
        return "Error: Resume text is empty."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"

    prompt = f"""
    From the following resume text, extract only the full name of the person.
    The name is usually at the very top of the document.
    Return just the full name and nothing else. Do not add any labels, explanations, or other words.

    Resume Text:
    ---
    {resume_text}
    ---
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        response_data = response.json()

        if 'candidates' in response_data and response_data['candidates']:
            content = response_data['candidates'][0].get('content', {})
            if 'parts' in content and content['parts']:
                extracted_text = content['parts'][0].get('text', 'Could not extract name.').strip()
                if "sorry" in extracted_text.lower() or "unable" in extracted_text.lower():
                    return "Error: Model was unable to find a name in the text."
                return extracted_text

        return "Error: Could not find a valid name in the API response."
    except requests.exceptions.RequestException as e:
        return f"API Request Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred during the API call: {e}"

def extract_name_from_resume(text: str) -> str:
    """
    Public function used by other modules to extract name.
    Internally uses Gemini API via get_name_via_requests().
    """
    return get_name_via_requests(text, GEMINI_API_KEY)
