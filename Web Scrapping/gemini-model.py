import os
from openai import OpenAI
from scrapper import fetch_website_contents
from dotenv import load_dotenv
from IPython.display import Markdown, display

load_dotenv(override=True)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("No API key was found!")
elif not api_key.startswith("AIz"):
    print("An API key was found but it doesn't start with AIz")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it may have spaces at start or end.")
else:
    print("API key is found and Good to GO!")

gemini = OpenAI(base_url=GEMINI_BASE_URL, api_key=api_key)

system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related. Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

user_prompt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.
"""

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website}
    ]

def summarize(url):
    website = fetch_website_contents(url)
    response = gemini.chat.completions.create(
        model = "gemini-2.5-flash-lite",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

def display_summary(url):
    summary = summarize(url)
    display(Markdown(summary))
    print(summary)

display_summary("https://www.iplt20.com")