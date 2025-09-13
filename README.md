# 🌉 BridgeCMU

## Mission
BridgeCMU connects students with CMU alumni and professors based on their research interests and professional experiences. We hope to strengthen the Tartan community by streamlining the process of finding a mentor, research advisor, or referrer by providing an end-to-end service: developing profiles of students and alumni, matching them using semantic similarity metrics, and drafting emails proposing collaboration. By facilitating these targeted conversations, the tool enhances how students access guidance, share ideas, and build professional relationships. 

## Stack
### APIs
📖 **OpenAlex** - CMU-affiliated researcher names and interests

🦾 **CMU Directory** - CMU department affiliation

🔍 **Google Custom Search API** - Linkedin and YouTube links for alumni connections

### Models
⚡ **gemini-2.0-flash** - extracts keywords, drafts emails

🧠 **sentence-transformers/paraphrase-albert-small-v2** - embeds keywords into latent space

## Front-end
✨ **Streamlit** for the web app
