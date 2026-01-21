import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import gradio as gr
import sqlite3
from io import BytesIO
from PIL import Image
import requests
import pyttsx3

import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


load_dotenv(override=True)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
api_key = os.getenv('GROQ_API_KEY')

if api_key:
    print("API key is set and Good to Go!")
else:
    print("There was a problem fetching API key.")
    exit(0)

groq = OpenAI(base_url=GROQ_BASE_URL, api_key=api_key)
MODEL = 'openai/gpt-oss-20b'

DB = 'prices.db'

system_message = """ 
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

ticket_prices = {"london": "$250", "paris": "$ 320", "america": "$400", "australia": "$450"}

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS prices (city TEXT PRIMARY KEY, price TEXT)")
    conn.commit()

def set_ticket_price(city, price):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prices (city, price) VALUES (?, ?) ON CONFLICT(city) DO UPDATE SET price = ?', (city.lower(), price, price))
        conn.commit()

for city, price in ticket_prices.items():
    set_ticket_price(city, price)

def get_ticket_price(city):
    print(f"DATABASE TOOL CALLED: Getting price for {city}", flush=True)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT price FROM prices WHERE city = ?', (city.lower(),))
        result = cursor.fetchone()
        return f"Ticket price to {city} is {result[0]}" if result else "No price data available for this city"

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of return ticket to the destination city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city that the customer wants to travel to"
            }
        },
        "required": ["city"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": price_function}]

# IMAGE GENERATION

hf_api_key = os.getenv('HF_API_KEY')

def artist(city):
    prompt = f"""
    A vibrant pop-art style illustration of a vacation in {city},
    showing famous landmarks, tourist attractions, culture,
    colorful scenery, cinematic lighting
    """

    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {hf_api_key}"
    }

    payload = {"inputs": prompt}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)

        print("HF status:", response.status_code)
        print("HF content-type:", response.headers.get("Content-Type"))

        if response.status_code != 200:
            print("HF error body:", response.text)
            return None

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            print("HF non-image response:", response.text)
            return None

        return Image.open(BytesIO(response.content))

    except Exception as e:
        print("HF exception:", e)
        return None


# TEXT TO SPEECH GENERATION

def talker(message):
    try:
        engine = pyttsx3.init()
        engine.save_to_file(message, "speech.wav")
        engine.runAndWait()
        engine.stop()
        return "speech.wav"
    except Exception as e:
        print("TTS error:", e)
        return None


def chat(history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history
    response = groq.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    cities = []
    image = None

    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        responses, cities = handle_tool_calls_and_return_cities(message)
        messages.append(message)
        messages.extend(responses)
        response = groq.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    
    reply = response.choices[0].message.content
    history += [{"role": "assistant", "content": reply}]

    voice = talker(reply)

    if cities:
        image = artist(cities[0])
        if image is None:
            image = None
    
    return history, voice, image

def handle_tool_calls_and_return_cities(message):
    responses = []
    cities = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('city')
            cities.append(city)
            price_details = get_ticket_price(city)
            responses.append({
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            })

    return responses, cities


def put_message_in_chatbot(message, history):
    return "", history + [{"role": "user", "content": message}]

with gr.Blocks() as ui:
    with gr.Row():
        chatbot = gr.Chatbot(height=500)
        image_output = gr.Image(height=500, interactive=False)
    
    with gr.Row():
        audio_output = gr.Audio(autoplay=True)
    
    with gr.Row():
        message = gr.Textbox(label="Chat with our FlightAI Assistant: ")
    
    message.submit(put_message_in_chatbot, inputs=[message, chatbot], outputs=[message, chatbot]).then(fn=chat, inputs=chatbot, outputs=[chatbot, audio_output, image_output])

ui.launch(
    inbrowser=True,
    auth=("nithin", "0704"),
    server_name="127.0.0.1",
    server_port=7860,
    show_error=True
)
