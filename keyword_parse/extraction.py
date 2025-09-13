import os
import requests
import re
import pickle
from typing import List, Dict
from .comparison import get_top_similar_profs  # your optimized prof matching
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_keywords_from_document(resume_text: str) -> List[str]:
    """
    Extract research interests / keywords from a document using Gemini API.
    Returns a list of lowercase keywords.
    """
    prompt = f"""
    Extract the most important research interests, topics, and skills from the following text.
    Return only a Python-style list of keywords (lowercase, no explanations).

    Text:
    \"\"\"{resume_text}\"\"\"
    """
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    
    response = requests.post(GEMINI_URL, headers=headers, json=data)
    response.raise_for_status()
    
    resp_json = response.json()
    
    # Extract text safely
    output_text = ""
    try:
        output_text = resp_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError):
        raise ValueError(f"No text found in Gemini API response: {resp_json}")
    
    # Remove markdown code fences if present
    output_text = re.sub(r"^```(?:python)?", "", output_text.strip())
    output_text = re.sub(r"```$", "", output_text.strip())
    
    # Parse into list
    try:
        keywords = eval(output_text)
        if isinstance(keywords, list):
            return [kw.lower().strip() for kw in keywords]
        else:
            return []
    except:
        # fallback: comma split
        return [kw.strip().lower() for kw in output_text.split(",")]

def draft_email_to_prof(student_keywords: List[str], stu_name: str, stuid: str, matched_interests: List[str], prof_name: str) -> str:
    """
    Uses Gemini API to draft a personalized email to a professor.
    """
    prompt = f"""
    Draft a professional and polite email to Professor {prof_name} expressing interest
    in their research. The student has the following research interests: {student_keywords}.
    They share these specific matched interests with the professor: {matched_interests}.
    Their name is {stu_name} and Andrew ID is {stuid} (student id at CMU).
    Keep it concise, 3-5 sentences, and include a polite request to discuss research opportunities.
    """

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(GEMINI_URL, headers=headers, json=data)
    response.raise_for_status()
    resp_json = response.json()

    # Extract text safely
    output_text = ""
    try:
        output_text = resp_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError):
        raise ValueError(f"No text found in Gemini API response: {resp_json}")

    # Remove markdown/code fences if any
    output_text = re.sub(r"^```(?:python)?", "", output_text.strip())
    output_text = re.sub(r"```$", "", output_text.strip())
    
    return output_text


# ---------------- Example workflow ----------------
if __name__ == "__main__":
    # 1. Load student resume text
    student_resume = """
    I am a computer science student interested in machine learning, robotics, 
    reinforcement learning, and natural language processing. I have experience 
    with Python, TensorFlow, and PyTorch.
    """

    # 2. Extract student keywords
    student_keywords = get_keywords_from_document(student_resume)
    print("Extracted Student Keywords:", student_keywords)

    # 3. Find top professors
    top_profs = get_top_similar_profs(student_keywords, threshold=0.3, prof_data_path=".prof_data.pkl")
    
    # 4. Draft emails for each prof
    for prof in top_profs:
        prof_name = prof['prof_name']
        matched_interests = prof['matched_interests']
        email_text = draft_email_to_prof(student_keywords, matched_interests, prof_name)
        print(f"\n--- Email to {prof_name} ---\n{email_text}\n")
        
# Example usage
if __name__ == "__main__":
    resume_text = """
    I am a computer science student interested in machine learning, robotics, 
    reinforcement learning, and natural language processing. I have experience 
    with Python, TensorFlow, and PyTorch.
    """
    keywords = get_keywords_from_document(resume_text)
    print(keywords)


