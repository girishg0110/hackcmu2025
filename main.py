import streamlit as st

from st_utils import extract_text_from_pdf, get_mailto
from keyword_parse.extraction import get_keywords_from_document, get_top_similar_profs, draft_email_to_prof

top_k_profs = 5
get_top_similar_profs(['a'])

st.title("Research Matcher")

with st.form('student_submission') as form:
    name = st.text_input('Name')
    stuid = st.text_input('Andrew ID')
    interests = st.text_area('Research Interests')
    files = st.file_uploader('Files (your resume, statement of purposes, past papers, diary entries...)', type='pdf', accept_multiple_files=True)
    submit_button = st.form_submit_button()

# Read resume
if files:
    with st.spinner('Reading your files...'):
        full_text = '\n\n'.join(map(extract_text_from_pdf, files))

    with st.spinner("Extracting keywords from documents..."):
        stu_keywords = get_keywords_from_document(full_text)

    with st.spinner("Comparing your keywords to our database..."):
        profs = get_top_similar_profs(stu_keywords)
        profs = sorted(profs, key = lambda x: x['similarity_score'], reverse=True)
        prof_cards = []
        for i in range(min(top_k_profs, len(profs))):
            # display prof_i
            p = profs[i]
            with st.expander(p['prof_name']):
                st.header(p['prof_name'])
                st.write("Department:", p['prof_dpt'].upper())
                st.write(f"Email:", p['prof_email'])
                st.write(f"Similarity: {p['similarity_score'] * 100:.1f}%\n")
                st.write("Professor Interests:", ', '.join(p['prof_keywords']))
                st.write(f"Matched interests:", ', '.join(p['matched_interests']).lower())
                if st.button("Generate email", key=f'prof_email_generate_{i}'):
                    draft_email = draft_email_to_prof(stu_keywords, name, stuid, p['matched_interests'], p['prof_name'])
                    email = p['prof_email']
                    subject = f'Research proposal for {p["prof_email"]}'
                    body = draft_email

                    st.write(f"To: {email}")
                    st.write(f"Subject: {subject}")
                    st.text_area(body)
                    
                    mailto_url = get_mailto(email, subject, body)
                    st.link_button('Send email from Outlook', mailto_url)