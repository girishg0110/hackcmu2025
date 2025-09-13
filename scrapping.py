# Saves author names, research topics, dept_name and email into a json file
import requests
import json
import time
import requests
from bs4 import BeautifulSoup
import unicodedata

def get_prof_email_and_dpt(full_name):
    json = {
        'search': full_name, 'action': 'Search', 
        'searchtype': 'basic', 'activetab': 'basic'
    }
    try:
        prof_data = requests.post('https://directory.andrew.cmu.edu/index.cgi', data=json)
        soup = BeautifulSoup(prof_data.content, features = 'html.parser')
        email = soup.find("b", string="Email:").next_sibling.strip()
        print(email)
        dpt = soup.find("b", string="Department with which this person is affiliated:").next_sibling.next_sibling
        print(dpt)
        return {'prof_email': email, 'prof_dpt': dpt}
    except:
        email = '.'.join(full_name.replace('.', '').lower().split()) + '@cs.cmu.edu'
        dpt = 'Unknown'
        return {'prof_email': email, 'prof_dpt': dpt}


def remove_diacritics(input_str):
    return ''.join(c for c in unicodedata.normalize('NFD', input_str) if unicodedata.category(c) != 'Mn')


# Extract author IDs from multiple pages in intervals of 10
all_author_ids = []

for page in range(10, 1001, 10):  
    url = f"https://api.openalex.org/authors?page={page}&filter=last_known_institutions.id:i74973139&sort=works_count:desc&per_page=10"
    response = requests.get(url)
    data = response.json()
    
    for author in data.get('results', []):
        all_author_ids.append(author['id'])
    
    if not data.get('results', []):
        print(f"No more results found at page {page}")
        break
    time.sleep(0.1)

print(f"Extracted {len(all_author_ids)} author IDs from pages")

# Collect author names and topics
authors_data = []

for i, author_id in enumerate(all_author_ids):
    author_code = author_id.split('/')[-1]
    
    print(f"Fetching detailed data for author {i+1}/{len(all_author_ids)}: {author_code}")
    
    detail_url = f"https://api.openalex.org/people/{author_code}"
    detail_response = requests.get(detail_url)
    
    if detail_response.status_code == 200:
        author_detail = detail_response.json()
        
        author_name = author_detail.get('display_name', 'Unknown')
        author_name = remove_diacritics(author_name)
        name_split = author_name.split()
        
        # Filter names with less than 2 parts or first name < 3 characters
        if len(name_split) < 2 or len(name_split[0]) <3:
            print(f"Unexpected author name format: {author_name}, skipping...")
            continue

        topics = author_detail.get('topics', [])
        
        topic_names = [topic.get('display_name', 'Unknown') for topic in topics[:5]]

        author_info = get_prof_email_and_dpt(author_name)
        authors_data.append({
            'prof_name': author_name,
            'prof_keywords': topic_names,
            'prof_email': author_info['prof_email'],
            'prof_dpt': author_info['prof_dpt']
        })
        
        print(f"  - {author_name}: {len(topic_names)} topics")
        
    else:
        print(f"Failed to fetch data for {author_code}: {detail_response.status_code}")
        authors_data[author_code] = {
            'name': 'Failed to fetch',
            'topics': []
        }
    
    time.sleep(0.2)

with open('authors_and_topics.json', 'w') as f:
    json.dump(authors_data, f, indent=2)

print(f"\nFinal results saved to 'authors_and_topics.json'")
print(f"Successfully collected data for {len(authors_data)} authors")

