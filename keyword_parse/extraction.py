import os
import requests
import re
import pickle
from typing import List, Dict
from comparison import get_top_similar_profs  # your optimized prof matching
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


def draft_email_to_prof(
    student_keywords: List[str],
    stu_name: str,
    stuid: str,
    resume_text: str,
    matched_interests: List[str],
    prof_name: str
) -> str:
    """
    Uses Gemini API to draft a personalized email to a professor, alum, or student.
    The tone is: came across your work, interested in connecting, and highlighting overlaps.
    """
    prompt = f"""
    Draft a professional and thorough email to {prof_name} from the perspective of a CMU student.
    The student's name is {stu_name} and his/her Andrew ID is {stuid}.

    Student details (resume text):
    {resume_text}

    Student research interests / keywords: {student_keywords}.
    Shared interests with {prof_name}: {matched_interests}.

    The email should:
    - Say the student came across their work and is very interested.
    - Highlight overlaps in research / professional / matched interests above and past experiences from the resume.
    - Elaborates on 1-2 experiences from the resume and explains accomplishments and connection to the professor's work.
    - Politely ask if they'd be available for a chat or to connect.
    - Be friendly and tailored to the student's background.
    - GIVE ME THE FINAL EMAIL ONLY, NO EXPLANATIONS OR MARKDOWN OR [], SOMETHING WHICH I CAN SEND DIRECTLY.
    """
    print(prompt)
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
    with Python, TensorFlow, and PyTorch. I also worked on an autonomous drone
    navigation project using visual-inertial odometry and Kalman filtering.
    """

    # 2. Extract student keywords
    student_keywords = get_keywords_from_document(student_resume)
    print("Extracted Student Keywords:", student_keywords)

    # 3. Find top matches (professors/alumni/students)
    top_profs = get_top_similar_profs(student_keywords, threshold=0.3, prof_data_path="prof_data.pt")
    
    # 4. Draft emails for each prof
    for prof in top_profs[0:1]:
        prof_name = prof['prof_name']
        matched_interests = prof['matched_interests']
        email_text = draft_email_to_prof(
            student_keywords,
            stu_name="John Doe",
            stuid="jdoe",
            resume_text=student_resume,
            matched_interests=matched_interests,
            prof_name=prof_name
        )
        print(f"\n--- Email to {prof_name} ---\n{email_text}\n")
