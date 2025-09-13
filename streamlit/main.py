import streamlit as st
import time
import pymupdf
from streamlit_card import card as Card

# Utils
get_keywords_from_document = lambda text: []
get_top_similar_profs = lambda keywords_list: [
    {
        'prof_name' : 'Ronald Karp',
        'prof_keywords' : ['computer vision', 'statistics', 'cheesemaking'],
        'prof_contact' : 'ronaldkarp@cs.cmu.edu',
        'similarity_score' : 0.96345
    }
] # List[Dict[prof_name : str, prof_keywords : List, prof_contact : str]]
top_k = 5

def extract_text_from_pdf(pdf_file):
    doc = pymupdf.Document(stream=pdf_file)
    text = ""
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
        
    return text

def get_mailto(email, keywords_list):
    # mailto:email&subject=subject&body=body
    email = email
    subject = "Proposal for Research Collaboration"
    body = 
    return f"mailto:{email}&subject={subject}&body={body}"

st.title("Research Matcher")

with st.form('student_submission') as form:
    name = st.text_input('Name')
    interests = st.text_area('Research Interests')
    files = st.file_uploader('Files (your resume, statement of purposes, past papers, diary entries...)', type='pdf', accept_multiple_files=True)
    submit_button = st.form_submit_button()

# Read resume
if files:
    with st.spinner('Reading your files...'):
        full_text = '\n\n'.join(map(extract_text_from_pdf, files))
        st.write(full_text)

    with st.spinner("Extracting keywords from documents..."):
        # Get keywords from resume
        all_keywords = get_keywords_from_document(full_text)
        # st.write(all_keywords)

    with st.spinner("Comparing your keywords to our database..."):
        profs = get_top_similar_profs(all_keywords)
        profs = sorted(profs, key = lambda x: x['similarity_score'], reverse=True)
        prof_cards = []
        for i in range(min(top_k, len(profs))):
            # display prof_i
            p = profs[i]
            prof_cards.append(
                Card(
                    title = p['prof_name'],
                    text = f"Similarity: {p['similarity_score'] * 100:.1f}%\n" + ', '.join(p['prof_keywords']),
                    url = 'mailto:' + p['prof_contact']
                )
            )
            if prof_cards[i]:
                st.write("Clicked", i)