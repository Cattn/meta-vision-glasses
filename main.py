import time
import mouse
from PIL import ImageGrab
import pyautogui
from openai import OpenAI
import clipman

client = OpenAI(api_key="YOUR_KEY_HERE")
clipman.init()

def take_screenshot():
    time.sleep(1)
    mouse.move("696", "950", True, 0.4)
    mouse.click()
    mouse.move("960", "540", True, 0.4)
    time.sleep(1)
    mouse.right_click()
    
    mouse.move("10", "128", False, 1)
    mouse.click()

    mouse.move("100", "300", True, 0.2)
    mouse.click()
    return clipman.get()

def sendMessage(message):
    time.sleep(1)
    mouse.move("850", "1020", True, 0.3)
    mouse.click()
    clipman.set(message)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.hotkey('enter')

def process_screenshot_url(url):
    completion = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Try and find any text in the image. Once you do, if it's a long paragraph or text, summarize the key points of it. If there is no text, then ignore this and do not tell me that you found no text. If there is no descernable text, try and briefly describe the image, including any people, types of animals (give a guess to a breed if it is a cat or dog), or other info. Also provide any other helpful information."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url,
                        },
                    },
                ],
            }
        ],
    )
    sendMessage(completion.choices[0].message.content)

region_of_screen = (600, 900, 700, 1000)

while True:
    img1 = ImageGrab.grab(bbox=region_of_screen)
    
    while True:
        time.sleep(1)
        img2 = ImageGrab.grab(bbox=region_of_screen)

        if img1 != img2:
            screenshot_url = take_screenshot()
            process_screenshot_url(screenshot_url)
            break


    img1 = ImageGrab.grab(bbox=region_of_screen)