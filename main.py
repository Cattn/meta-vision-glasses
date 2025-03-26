import os
import asyncio
import aiohttp
import time
import random
import json
import tempfile
import re
import mouse 
import base64
import traceback
import aiofiles
import pyautogui
from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import async_playwright
import html
from pydub import AudioSegment

load_dotenv()

with open("config.json", "r") as f:
    config = json.load(f)

mode = config["default_mode"]
global_browser = None
last_image_url = None
model = config["default_model"]

client = OpenAI(api_key=os.getenv("API_KEY"))

# todo: rewrite nav, exit, send to use focus/playwright
def nav_to_image():
    mouse.move("635", "850", True, 0.3)
    mouse.click()
    time.sleep(0.5)

def exit_image():
    mouse.move("100", "300", True, 0.2)
    mouse.click()

def send_message(message):
    global mode
    time.sleep(1.5)

    pyautogui.click(x=850, y=1020)  
    time.sleep(0.4)

    if mode == "discord":
        pyautogui.write(message, interval=0.02)
        pyautogui.press('enter')
        return

    lines = message.split('\n')
    for i, line in enumerate(lines):
        if line:
            pyautogui.write(line, interval=random.uniform(0.0005, 0.001))
        if i < len(lines) - 1:
            pyautogui.hotkey('shift', 'enter')
            time.sleep(0.003)

    pyautogui.press('enter')
    time.sleep(1)

async def send_disc_message(person, message):
    print("send_disc_message called")
    if person.endswith("."):
        person = person[:-1]
    print(person)

    disc_page = await global_browser.new_page()
    
    user_urls = {user: str(user_id) for entry in config["users"] for user, user_id in entry.items()}

    if person not in user_urls:
        print(f"Unknown recipient: {person}")
        await disc_page.close()
        return
    
    await disc_page.goto(f"https://discord.com/channels/@me/{user_urls[person]}")
    await disc_page.wait_for_load_state('domcontentloaded')
    
    await asyncio.sleep(2)
    
    pyautogui.click(x=850, y=1020)  
    time.sleep(0.5)

    send_message(message)
    await asyncio.sleep(1)
    await disc_page.close()

async def switchModel(message):
    global model
    if message.lower() == "chat gpt" or message.lower() == "chatgpt" or message.lower() == "chatgpt-4o-latest":
        model = "chatgpt-4o-latest"
    elif message.lower() == "a cheaper one" or message.lower() == "a cheaper model" or message.lower() == "gpt-4o-2024-08-06":
        model = "gpt-4o-2024-08-06"
    # elif message.lower() == "search" or message.lower() == "search model" or message.lower() == "gpt-4o-search-preview-2025-03-11":
    #    model = "gpt-4o-search-preview-2025-03-11"  # bruh why is this so expensive lol
    elif message.lower() == "cheap search" or message.lower() == "cheap search model" or message.lower() == "gpt-4o-mini-search-preview-2025-03-11":
        model = "gpt-4o-mini-search-preview-2025-03-11"
    else:
        model = config["default_model"]
    print(f"Model changed to {model}")

async def handle_command(command):
    try:
        global mode
        global last_image_url
        print(command)
        print(f"Mode: {mode}")
        command_words = command.split(" ")
        if command_words[-1].endswith("."):
            command_words[-1] = command_words[-1][:-1]
        command = " ".join(command_words)
        
        if command.lower().startswith("switch mode to") or command.lower().startswith("change mode to"):
            mode = command.split(" ")[3]
            print(f"Mode changed to {mode}")
            return
        if command.lower().startswith("send message to") and mode == "discord":
            message = " ".join(command.split(" ")[4:])
            message = html.unescape(message)
            await send_disc_message(command.split(" ")[3].lower(), message)
            return
        if command.lower().startswith("send image to") and mode == "discord":
            message = last_image_url
            await send_disc_message(command.split(" ")[3].lower(), message)
            return
        if command.lower().startswith("change model to") or command.lower().startswith("switch model to"):
            message = " ".join(command.split(" ")[3:])
            await switchModel(message)
            return
        print("sending prompt")
        await process_image(None, None, command)
    except Exception:
        print("Failed to process command")


async def get_image_url(page):
    print("Getting image source")
    await nav_to_image(page)
    await asyncio.sleep(1.5)

    img_element = await page.query_selector('img[src*="https"]')
    img_url = await img_element.get_attribute('src') if img_element else None

    await exit_image(page)
    return img_url

async def process_image(latest_image, seen_images, text):
    global mode
    global last_image_url
    global model
    if mode == "discord":
        last_image_url = latest_image
        return
    if mode == "image":
        if latest_image and latest_image not in seen_images:
            seen_images.add(latest_image)
            completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Try and find any text in the image. Once you do, if it's a long paragraph or text, summarize the key points of it. If it's a math question or other question, answer and provide the solution with a brief explanation. If there is no text, then ignore this and do not tell the user that you found no text AT ALL COSTS. If there is no descernable text, try and briefly describe the image, including any people, types of animals (give a guess to a breed if it is a cat or dog), or other info. Also provide any other helpful information. Keep your answers relatively short, do not use markdown or latex with math. Try and format it well without markdown. Try and be generally concise, unless you are answering a problem or doing math, try and limit to around 2 paragraphs. Also, if it is just an envrionment or scenery, try and describe with detail the scenery, pointing out at least on unique thing. Your primary goal is to be helpful to the user and assist them in any problem, or help them to describe anything depicted.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here's my image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": latest_image,
                            },
                        },
                    ],
                }
            ],
        )
        send_message(completion.choices[0].message.content)
        return
    if mode == "text":
        print("running: " + text)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Your name is Charles. You are a helpful assistant. Your goal is to answer any question the user might have, while being concise. Try and format it well without markdown. Try and be generally concise.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ],
                }
            ],
        )
        send_message(completion.choices[0].message.content)
        return
    
async def process_audio(latest_audio, seen_audios):
    if latest_audio and latest_audio not in seen_audios:
        seen_audios.add(latest_audio)

        async with aiohttp.ClientSession() as session:
            async with session.get(latest_audio) as response:
                if response.status == 200:
                    audio_data = await response.read()
                else:
                    print(f"Failed to download audio: {response.status}")
                    return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_path = temp_audio_file.name

        try:
            audio = AudioSegment.from_file(temp_audio_path, format="mp4")
            temp_converted_path = temp_audio_path.replace(".mp4", ".wav")
            audio.export(temp_converted_path, format="wav")

            async with aiofiles.open(temp_converted_path, "rb") as audio_file:
                audio_content = await audio_file.read()

            audio_base64 = base64.b64encode(audio_content).decode("utf-8")

            completion = client.chat.completions.create(
                model="gpt-4o-mini-audio-preview-2024-12-17",
                messages=[
                    {
                        "role": "system",
                        "content": "Try to describe the audio. If it's a song, identify its features. If it's a person asking a question, answer it. Otherwise, describe the audio."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here's my audio."},
                            {"type": "input_audio", "input_audio": {"data": audio_base64, "format": "wav"}}
                        ]
                    }
                ]
            )

            send_message(completion.choices[0].message.content)

        except Exception as e:
            print(f"Error during API call: {e}")
            traceback.print_exc()
        
        finally:
            os.remove(temp_audio_path)
            os.remove(temp_converted_path)

async def main():
    user_data_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel='chrome',
            args=[f"--profile-directory=Profile {config['chrome_profile']}", "--start-maximized"],
            headless=False,
            no_viewport=True
        )

        global global_browser
        global_browser = browser
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto(config["messenger_link"])
        await page.wait_for_load_state('load')

        image_queue = []
        seen_images = set()
        request_processing_enabled = False
        
        audio_queue = []
        seen_audios = set()

        def is_valid_image_url(url):
            return (
                url.startswith("https://scontent-") and
                "fbcdn.net" in url and
                "100x100" not in url and
                re.search(r'(\.jpg|\.png|\.jpeg)', url)
            )
            
        def is_valid_audio_url(url):
            return (
                url.startswith("https://cdn.fbsbx.com/v/t59.3654-21/") and
                ".mp4" in url and
                "audioclip" in url and
                "dl=1" in url
        )

        async def on_request(request):
            nonlocal request_processing_enabled
            if not request_processing_enabled:
                return
            
            url = request.url
            if is_valid_image_url(url):
                image_queue.append(url)
                if len(image_queue) > 5: 
                    image_queue.pop(0)

                latest_image = image_queue[-1]
                await process_image(latest_image, seen_images, None)
            
            if is_valid_audio_url(url):
                audio_queue.append(url)
                if len(audio_queue) > 5: 
                    audio_queue.pop(0)

                latest_audio = audio_queue[-1]
                await process_audio(latest_audio, seen_audios)

        page.on("request", lambda request: asyncio.create_task(on_request(request)))

        await asyncio.sleep(6) # need to be put in otherwise any image that loads during page load will be used (bad), sadly page load event listener sucks
        request_processing_enabled = True
        print("Request processing now enabled.")
        print("Scanning for new images...")
        selector = ".x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x1ji0vk5.x18bv5gf.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1xmvt09.x6prxxf.x1fcty0u.xw2npq5.xudqn12.x3x7a5m.xq9mrsl"
        
        latest_inner_html = None
        latest_element = None
        
        while True:
            await asyncio.sleep(1)  # wait for 1 second before checking for new elements
            new_elements = await page.query_selector_all(selector)
            if new_elements:
                latest_element = new_elements[-1]  # get the most recent element
                child_div = await latest_element.query_selector("div")
                if child_div:
                    inner_html = await child_div.inner_html()
                    if inner_html != latest_inner_html:
                        latest_inner_html = inner_html
                        await handle_command(inner_html)
                
if __name__ == "__main__":
    asyncio.run(main())