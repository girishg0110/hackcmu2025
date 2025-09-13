import pymupdf

def extract_text_from_pdf(pdf_file):
    doc = pymupdf.Document(stream=pdf_file)
    text = ""
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
        
    return text

def get_mailto(email, subject, body):
    return f"mailto:{email}&subject={subject}&body={body}"
