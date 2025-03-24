import os
import asyncio
import time
import random
import re
import mouse 
import pyautogui
from openai import OpenAI
from playwright.async_api import async_playwright

client = OpenAI(api_key="YOUR_API_KEY")

# todo: rewrite nav, exit, send to use focus/playwright
def nav_to_image():
    mouse.move("635", "850", True, 0.3)
    mouse.click()
    time.sleep(0.5)

def exit_image():
    mouse.move("100", "300", True, 0.2)
    mouse.click()

def send_message(message):
    print("sendMessage called")
    mouse.move("850", "1020", True, 0.2)
    mouse.click()

    lines = message.split('\n')
    for i, line in enumerate(lines):
        if line:
            pyautogui.write(line, interval=random.uniform(0.0001, 0.0003))
        if i < len(lines) - 1:
            pyautogui.hotkey('shift', 'enter')
            time.sleep(0.003)

    pyautogui.press('enter')

async def handle_command(element):
    try:
        if await element.get_attribute("role") == "grid":
            return True

        a_selector = "div:nth-child(2) > div:nth-child(2) > div > div > span > div:nth-child(2) > div > div > a"
        if await element.query_selector(a_selector):
            return False

        text_elements = await element.query_selector_all('div[dir="auto"][class*="x1yc453h"]')
        for text_element in text_elements:
            inner_text = (await text_element.inner_text()).strip()
            if inner_text:
                print(f"Found text: {inner_text}")
                return True

        return False
    except Exception:
        print("Failed to find text")
        return True

async def get_image_url(page):
    print("Getting image source")
    await nav_to_image(page)
    await asyncio.sleep(1.5)

    img_element = await page.query_selector('img[src*="https"]')
    img_url = await img_element.get_attribute('src') if img_element else None

    await exit_image(page)
    return img_url

async def process_image(latest_image, seen_images):
    if latest_image and latest_image not in seen_images:
        seen_images.add(latest_image)
        completion = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", # todo: make prompt better it sucks rn
                        "text": "Try and find any text in the image. Once you do, if it's a long paragraph or text, summarize the key points of it. If it's a math question or other question, answer and provide the solution with a brief explanation. If there is no text, then ignore this and do not tell me that you found no text. If there is no descernable text, try and briefly describe the image, including any people, types of animals (give a guess to a breed if it is a cat or dog), or other info. Also provide any other helpful information. Keep your answers relatively short, do not use markdown or latex with math. Try and format it well without markdown. Try and be as concise as possible."
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

async def main():
    user_data_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel='chrome',
            args=["--profile-directory=Profile 3"],
            headless=False
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto("https://www.messenger.com/t/9293726437413424")
        await page.wait_for_load_state('load')

        image_queue = []
        seen_images = set()
        request_processing_enabled = False

        def is_valid_image_url(url):
            return (
                url.startswith("https://scontent-") and
                "fbcdn.net" in url and
                "100x100" not in url and
                re.search(r'(\.jpg|\.png|\.jpeg)', url)
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
                await process_image(latest_image, seen_images)

        page.on("request", lambda request: asyncio.create_task(on_request(request)))

        await asyncio.sleep(6) # need to be put in otherwise any image that loads during page load will be used (bad), sadly page load event listener sucks
        request_processing_enabled = True
        print("Request processing now enabled.")
        print("Scanning for new images...")

        while True:
            await asyncio.sleep(2) # can be changed, prob isn't needed bec glasses are slow

if __name__ == "__main__":
    asyncio.run(main())