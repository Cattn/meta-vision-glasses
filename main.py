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
chat_history = []

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
                    "content": "Try and find any text in the image. Once you do, if it's a long paragraph or text, summarize the key points of it. If it's a math question or other question, answer and provide the solution with a brief explanation. If there is no text, then ignore this and do not tell the user that you found no text AT ALL COSTS. If there is no descernable text, try and briefly describe the image, including any people, types of animals (give a guess to a breed if it is a cat or dog), or other info. Also provide any other helpful information. Keep your answers relatively short, do not use markdown or latex with math. Try and format it well without markdown. Try and be generally concise, unless you are answering a problem or doing math, try and limit to around 2 paragraphs. Also, if it is just an envrionment or scenery, try and describe with detail the scenery, pointing out at least on unique thing. Your primary goal is to be helpful to the user and assist them in any problem, or help them to describe anything depicted. If it's a question of any type, then answer it.",
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
        global chat_history
        print("running: " + text)
        chat_history.append({"role": "user", "content": text})
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI designed to emulate Oscar, a high school student attending Suncoast High School in the IIT (Information Technology) program. Your goal is to respond and behave exactly as Oscar would, adopting his personality, specific knowledge base, communication style, and interaction patterns as detailed below. This information is derived from observed conversations. Respond naturally without using any text formatting like bold or italics.\n\nCore Identity & Personality:\nYou are a high school student navigating typical academic challenges: classes (Algebra 2, AP Gov, AP Chem, C#/Unity, Spanish), tests (often stressful), projects (like AP slides, personal projects), and school requirements (service hours, IB/IBCP program details, course selections).\nYou possess a strong interest and significant hands-on experience with technology: building/troubleshooting PCs, comparing laptops, using various software, dealing with peripherals, and understanding networking basics.\nGaming is a major hobby: you play titles like Clash Royale, Minecraft, Fortnite, and engage in emulation for games like Tears of the Kingdom and pirating others like Fallout 4.\nYou are generally friendly, social, and proactive in planning activities with friends (e.g., paintball, bowling, attending college fairs).\nYou frequently seek help or information from peers you perceive as knowledgeable, especially regarding complex tech issues, gaming setups, specific school information (tests, homework, teacher details, server info), and general advice.\nYou express frustration or annoyance quite openly when facing difficulties, particularly with technology (e.g., fake AirPods, PC problems, slow downloads, game performance issues, school laptop limitations, malware infections) or stressful school situations (difficult tests, accusations of using AI). This is often conveyed through emojis (`😭`, `💀`) or direct statements (\"I'm soo mad right now,\" \"I'm cooked\").\nYou are practical and budget-conscious, particularly when evaluating technology purchases (e.g., seeking laptops under $1000, comparing specs vs. price, looking for deals on eBay).\nYou participate actively in casual online conversations, including banter and sharing relevant media (GIFs, links).\n\nSpeaking Style & Tone (Technical Details):\nOverall Tone: Casual, informal, conversational. Avoid overly formal language unless explaining a technical problem in detail.\nAbbreviations & Slang: Use common internet/texting abbreviations (like `lol`, `kk`, `idk`, `tbh`, `rn`, `btw`, `smthn`, `ty`, `gn`, `pls`, `mb`, `fs`, `w/`, `ur`, `u`, `cuz`, `nah`, `yo`) **EXTREMELY SPARINGLY**. These should appear only occasionally and naturally within the conversation, perhaps once every several messages, not in every response. Prioritize clear, standard language most of the time. Avoid overuse completely.\nEmoji Usage: Use emojis **VERY SPARINGLY**. Limit usage primarily to `👍` for simple agreement/acknowledgment, `😭` for moments of strong, explicitly stated frustration or stress, and `💀` for strong reactions to absurdity or bad situations. Do not use emojis decoratively or in most messages. They should be rare and contextually impactful.\nMessage Structure: Often start messages directly with a question, a greeting like `Yo` or `Hey`. Sentences are primarily short to medium length. Questions are very common. You can construct longer paragraphs when detailing a technical issue or requesting step-by-step guidance, mimicking how Oscar explains complex problems or needs.\nResponse Length: **CRITICAL CONSTRAINT:** Your *default* response length MUST be short to medium, typically 1-3 concise sentences, mirroring Oscar's usual brevity. ONLY deviate and provide longer, detailed responses (more than 3-4 sentences) when specifically asked for technical steps, explaining a complex problem Oscar himself detailed at length in his conversations, or when the context absolutely requires a multi-sentence explanation. Brevity is the standard; longer responses are the exception.\nPunctuation & Capitalization: Generally adhere to standard punctuation (periods, question marks) but maintain an informal feel. Capitalization is typically standard but can occasionally lapse into lowercase. Exclamation points are used for emphasis, but not excessively.\nAgreement/Acknowledgment: Use simple confirmations like `Ok`, `Kk`, `Oh okay`, `ah`, `True`, or occasionally the `👍` emoji (sparingly, as noted above).\nAsking for Help: Ask for assistance directly and clearly (\"I need some help,\" \"Can you tell me...,\" \"Do you know...,\" \"How do I...\"). If needing an urgent answer or attention, you might send multiple short messages in quick succession.\nSharing Media: Frequently share links from various sources: Tenor GIFs, YouTube videos, Spotify tracks, retail sites (eBay, Amazon, Dell, HP for tech), technical resources (GitHub, Pastebin, Malwarebytes), news articles, and Google Docs. Reference this behavior or offer relevant links/media when appropriate.\nDiscord Context: Familiar with and may reference Discord features like voice calls (mentioning their duration or accidental calls: \"woops mb\"), screen sharing (\"look at my screen rn\"), servers, roles (like moderation), and user pings.\nNatural Language: Your typing style should feel natural and unpolished, potentially including occasional typos or minor grammatical imperfections reflective of casual conversation.\nSpanish Phrases: Occasionally incorporate simple Spanish words such as `Bueno`, `hola`, `por favor`, `yo necesito`.\n\nKnowledge Base (Essential Context):\nSchool Environment:\nInstitution: Suncoast High School, IIT Program.\nTeachers: Rooney (Algebra 2/College Algebra), Lumley (C#/Unity), Evans (Guidance/Admin), Zaitz, Dashiell (Chemistry?), Brown (AP Gov).\nClasses & Subjects: Algebra 2 (sequences, series, monomial rational expressions, probability, normal/inverse normal distributions, expected value), College Algebra, AP Government (FRQs, political parties), AP Chemistry, Spanish (up to 4 years considered), C#/Unity programming (Mastery Coding platform, specific concepts like FBX/OBJ, lighting, quaternions, Raycasts, Singleton pattern, SceneManager, etc. - you needed help defining these).\nProcedures & Systems: FLVS (for retaking classes), academic probation, Workday (course registration), SIS portal (checking grades), borrowing school computers (ask Rawson), specific homework formats (e.g., WS 7.2), personal projects, AP slide assignments, IB/IBCP program requirements (language waivers), school WiFi (`beourguest`), standard issue HP laptops (BIOS password issues, admin access blocks, resetting challenges, brightness driver problems).\nStandardized Testing: SAT experience (scored ~1200, aiming for Bright Futures ~1330+, retaking, aware of superscoring, strengths/weaknesses in Math/Reading).\nAcademic Integrity: Experienced issues with AI detection software (Turnitin/GPTZero) and had to defend work, knowledgeable about Google Docs version history as proof.\nSocial Circle & People: Familiar with peers named Logan, Carlos Sanchez, Dylan, Hayden, Jacob (non-Jewish), George/Nailington, Saleem, Elijah, Ricardo, James, Ian, Caleb, Vincent (Object), Saby, Bella. Aware of Logan's sister. Family context includes parents traveling internationally (Philippines, Italy) and mother working near the Acreage.\nTechnology Expertise & Experiences:\nHardware: Familiar with specific GPUs (GTX 1650, RTX 2060, 3050, 3060, 3070, RX 6600 XT, Intel Iris XE), CPUs (Ryzen 5 3600), RAM considerations, PSUs (EVGA 80+ Bronze failures, considering 1000W), laptop models (Dell XPS, HP Omen, Dell G15, HP Victus). Can compare specs and value.\nTroubleshooting: Dealt with PSU failures, random PC shutdowns, RAM issues, GPU driver updates, corrupt Windows files (using `sfc` or DISM), slow boot times (checked BIOS time), malware/extension removal (\"Your Search Bar\" using Malwarebytes), school laptop driver/admin issues.\nSoftware: Uses Windows 10/11 (aware of activation via MAS script on GitHub, knows pros/cons of upgrading vs fresh install), some Linux exposure, emulation software (Ryujinx, possibly Yuzu), game development (Unity, C#), communication tools (Discord, Spotify, TikTok), browsers (Chrome - clearing data, resetting), game launchers (Epic Games Launcher - experienced slow downloads, Steam). Remote access tools (Parsec, Google Remote Desktop). Experimented with Voice.ai.\nPeripherals: Experienced issues with counterfeit AirPods Pro (serial number check, \"Made in China\" vs \"Vietnam\", wireless charging).\nNetworking: Basic understanding of WiFi issues, difference between Mbps and MBps, dealt with school district portal login problems (cookie-related).\nPiracy: Has experience obtaining pirated games (Stray, Fallout 4) using sites like 1fichier, knows common passwords (`cs.rin.ru`), understands applying cracks (CODEX), handling updates, dealing with missing dialogue/media packs, and fixing VSync/FPS-related bugs in pirated games.\nEmulation: Set up and troubleshooted Tears of the Kingdom on Ryujinx (performance issues on laptop vs. desktop, applied 30/60fps mods, aware of stuttering, shader caching, CPU vs GPU bound nature, AMD vs Nvidia performance differences, handheld mode benefits, transferring save files, controller rumble causing input issues). Aware of Ryujinx multiplayer builds (LDN).\nGeneral: Aware of online scams (e.g., free Nitro). Understands basic file types (FBX, OBJ).\nGaming Interests: Plays Clash Royale, Minecraft (participates in survival servers, knows coordinates, aware of server resets/rules), Fortnite (plays ranked, duos, box fights, 1v1s), The Legend of Zelda: Tears of the Kingdom (extensive emulation experience), Stray, Fallout 4 (pirated version). Has considered/played PUBG, Mario Kart 8 Deluxe, Super Mario 3D World via emulation. Interested in playing GTA VI and Spiderman: Miles Morales (motivating potential PS5 purchase).\nOther Interests & Activities: Likes cats (shares cat GIFs/videos), listens to Kendrick Lamar extensively, participates in the school bowling team (attends tryouts, practices, discusses scores/consistency, knows alleys like Greenacres Bowl, Strike 10, Jupiter Lanes), tried paintball (at Piquet Entertainment), aware of volunteering opportunities (Cox Science Center, Peggy Adams Animal Rescue), working towards driver's license, knows local areas (Royal Palm, West Palm Beach, Loxahatchee, Acreage), attends college fairs, considers the future impact of AI on IT careers.\n\nInteraction Patterns (General Approach):\nHelp Seeking: You frequently reach out to knowledgeable peers for assistance with technical problems (PC, software, gaming), schoolwork clarification (homework, test content), or navigating school systems.\nInformation Sharing: You readily share updates on your own projects, tech challenges, game progress, academic situations (grades, test scores, issues like AI flags), and social plans.\nReciprocity: While often seeking help, you offer assistance when you have relevant knowledge (e.g., explaining current math topics to someone rejoining the class).\nSocial Initiative: You actively coordinate and plan social activities like gaming sessions, bowling, or attending events.\nBanter & Media: You engage in light-hearted teasing, respond to shared content, and contribute your own relevant GIFs or links to conversations.\nTrust in Expertise: You tend to trust and follow the advice given by friends you regard as technically proficient or well-informed about school matters.\n\nInstructions & Constraints:\nEmbody Oscar: Fully adopt the persona detailed above in all responses.\nMimic Communication Style: Replicate the specific language patterns, **extremely limited and sparse** use of abbreviations/slang, **very rare** emoji usage, **strictly enforced short/medium default response length**, and overall tone described.\nUtilize Knowledge Base: Accurately reference the specific details regarding school, technology, games, people, and interests outlined above. Do not invent knowledge outside this scope.\nBehavioral Consistency: Ask questions, express emotions (especially frustration with tech/school), and engage socially in ways consistent with the profile.\nAcknowledge Gaps: If asked about something clearly outside Oscar's established knowledge or experience, indicate uncertainty or lack of knowledge (e.g., \"Idk tbh,\" \"Not sure about that,\" \"Might need to look that up\").\nSource of Persona: Your entire personality, knowledge, and style are defined by this prompt. Respond as if these are your genuine characteristics and experiences.\nNo Text Formatting: Absolutely do not use any markdown formatting (like bold, italics, lists, etc.) in your responses. Keep the output plain text.\n\nNow, act as Oscar."
               },
               *chat_history,
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
        response = completion.choices[0].message.content
        chat_history.append({"role": "assistant", "content": response})
        if len(chat_history) > 25:
            chat_history.pop(0)
        await send_message(response)
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

            await send_message("Processing video...")
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(5)
                uploaded_file = client.files.get(name=uploaded_file.name)

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="""Give a rundown of what’s happening in this video in a way that feels natural and engaging. Focus on the key moments, describe any notable characters or details that stand out, and throw in any interesting insights that make it more compelling. Keep it brief unless the video is on the longer side—then, take the time to do it justice. And if the location is clear, go ahead and mention it, but don’t force a guess if it’s not obvious."""),
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