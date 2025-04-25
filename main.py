import os
import asyncio
import aiohttp
import time
import json
import tempfile
import re
import base64
import traceback
import aiofiles
from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import async_playwright
import html
from pydub import AudioSegment
from google import genai
from google.genai import types

load_dotenv()

with open("config.json", "r") as f:
    config = json.load(f)

mode = config["default_mode"]
global_browser = None
last_image_url = None
model = config["default_model"]

client = OpenAI(api_key=os.getenv("API_KEY"))

async def send_message(message):
    global mode
    global global_browser
    time.sleep(1.5)
    
    page = global_browser.pages[0]

    if mode == "discord":
        div = await page.query_selector('.markup__75297.editor__1b31f.slateTextArea_ec4baf.fontSize16Padding__74017')
        if div:
            await div.click()
            await div.fill(message, force=True)
            await div.press('Enter')
        return

    div = await page.query_selector('.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x1iyjqo2.x1gh3ibb.xisnujt.xeuugli.x1odjw0f.notranslate')
    if div:
        await div.click()
        await div.fill(message)
        await div.press('Enter')
    else:
        print("Div not found")

async def send_disc_message(person, message):
    print("send_disc_message called")
    if person.endswith("."):
        person = person[:-1]
    print(person)

    disc_page = await global_browser.new_page()
    
    user_urls = {user: str(user_id) for entry in config["users"] for user, user_id in entry.items()}

    if person not in user_urls:
        send_message(f"Unknown recipient: {person}")
        await disc_page.close()
        return
    
    await disc_page.goto(f"https://discord.com/channels/@me/{user_urls[person]}")
    await disc_page.wait_for_load_state('domcontentloaded')
    
    await asyncio.sleep(2.5)

    await send_message(message)
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
        await send_message(completion.choices[0].message.content)
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
        await send_message(completion.choices[0].message.content)
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

            await send_message(completion.choices[0].message.content)

        except Exception as e:
            print(f"Error during API call: {e}")
            traceback.print_exc()
        
        finally:
            os.remove(temp_audio_path)
            os.remove(temp_converted_path)
            
async def process_video(latest_video, seen_videos):
    if latest_video not in seen_videos:
        seen_videos.add(latest_video)

        print("got video")

        async with aiohttp.ClientSession() as session:
            async with session.get(latest_video) as response:
                if response.status == 200:
                    video_data = await response.read()
                else:
                    print(f"Failed to download video: {response.status}")
                    return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(video_data)
            video_path = temp_video_file.name

        try:
            client = genai.Client(api_key=os.environ.get("GEM_KEY"))
            uploaded_file = client.files.upload(file=video_path)

            await send_message("Processing video: " + uploaded_file.name + "..." + "This may take a moment...")
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(5)
                uploaded_file = client.files.get(name=uploaded_file.name)

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="""Give a rundown of what’s happening in this video in a way that feels natural and engaging. Focus on the key moments, describe any notable characters or details that stand out, and throw in any interesting insights that make it more compelling. Keep it brief unless the video is on the longer side—then, take the time to do it justice. And if the location is clear, go ahead and mention it, but don’t force a guess if it’s not obvious. If you see any questions or problems in the video, attempt to give the answer in a good format. Give all answers. If it's a piece of media, try and identify and state what it is. If there is audio playing try to figure out what song or sound it is and describe/name it. If you cannot find any of these components, then simply do not mention then and write the rest as normal."""),
                    ],
                ),
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type=uploaded_file.mime_type,
                        ),
                    ],    
                ),
            ]

            response = client.models.generate_content(
                model="gemini-2.5-pro-exp-03-25",
                contents=contents,
            )

            await send_message(response.text)

        except Exception as e:
            print(f"Error during video processing: {e}")
            traceback.print_exc()

        finally:
            os.remove(video_path)

async def main():
    user_data_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel='chrome',
            args=[f"--profile-directory=Profile {config['chrome_profile']}", "--start-maximized"],
            headless=True,
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
        
        video_queue = []
        seen_videos = set()

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
            
        def is_valid_Video_url(url):
            return (
                url.startswith("https://video-mia3-1.xx.fbcdn.net/v/") or
                url.startswith("https://video-mia3-3.xx.fbcdn.net/v/") or
                url.startswith("https://video-mia3-2.xx.fbcdn.net/v/") and
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
                
            if is_valid_Video_url(url):
                video_queue.append(url)
                if len(video_queue) > 5: 
                    video_queue.pop(0)
                    
                latest_video = video_queue[-1]
                await process_video(latest_video, seen_videos)

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