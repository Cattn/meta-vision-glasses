# Meta Vision Glasses (Name Pending)

Let your glasses see for you! This tool allows you to get responses from images, text, and videos sent directly from your Meta Rayban glasses!

---

## 🚀 Installation

> It is highly recommended to use a virtual environment (venv).

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Install Playwright:
   ```sh
   playwright install
   ```

---

## 🛠 Setup

### 1️⃣ API Keys

Create a `.env` file in the root directory and add your OpenAI API key and Gemini API key:

```env
API_KEY=YOUR_OPENAI_API_KEY
GEM_KEY=YOUR_GEMINI_API_KEY
```

The program will automatically load these keys from the `.env` file.

### 2️⃣ Creating a New Chrome Profile for Playwright

1. Create a new Chrome profile dedicated to this application.
2. Depending on the order of creation (e.g., Profile 1 = first extra created), update the `chrome_profile` setting accordingly.
3. Log in to Discord via [discord.com/app](https://discord.com/app) with your desired account.
4. Log in to Messenger with the desired bot account.
5. **You still need to set up a user profile by logging in, but the browser will no longer need to remain open in the foreground.**

### 3️⃣ Configuration File

In your `config.json`, define users for quick access:

```json
{
    "users": [
        { "user1": 124124124141414 },
        { "friend": 129419248912489124 },
        { "cat": 2141249124818414 }
    ],
    "default_mode": "image",
    "default_model": "chatgpt-4o-latest",
    "chrome_profile": "1",
    "messenger_link": "https://www.messenger.com/t/1241414182481481"
}
```

- **User Nickname** (e.g., `friend`) = The name used to refer to them in voice commands.
- **Channel ID** = The direct message channel ID (not the user ID).
- **Default Mode** = Choose which mode you would like to be the default mode on startup.
- **Default Model** = The default AI model to use.
- **Chrome Profile** = The profile number for Playwright.
- **Messenger Link** = The Messenger conversation URL where messages will be sent.

---

## 🏃 Running the Program

Start the program using:

```sh
py main.py
```

The program now supports full headless mode! The browser will no longer need to remain open in the foreground.

---

## 📢 Usage

### 🎧 Communicating with ChatGPT

1. **Sending an Image:**
   - Say: *"Hey Meta, send a picture to [Account Name]"*.
   - Confirm the name.
   - Optionally, say: *"Hey Meta, read out my message"* to hear the response.

### 🎤 Voice Notes (Audio Mode)

- Any voice note sent (regardless of mode) will be processed by the preset model: `gpt-4o-mini-audio-preview-2024-12-17`.
- This model **cannot** be changed at this time.

### 🎥 Videos (Video Mode)

- Any video sent will be automatically processed using `gemini-2.5-pro-exp-03-25`.
- Ensure `GEM_KEY` is added to your `.env` file for this feature to function properly.
- The AI will generate insights, summaries, or descriptions based on the video content.

---

## 📝 Commands

### 🔄 Mode Switching

To switch between different modes, send a command:

```text
switch mode to {mode}
```

**Available Modes:**

- `image`: Send images only, get AI responses based on images.
- `text`: Send text messages, AI will respond as usual.
- `discord`: Stores image URLs for later use; no AI text/image processing.

### 📩 Messaging & Image Sending (Discord Mode Only)

- **Send a Message:**
  ```text
  send message to {nickname} {message}
  ```
- **Send an Image:**
  ```text
  send image to {nickname}
  ```

**Example Workflow:**

1. `switch mode to discord`
2. Send an image in chat.
3. `send image to {nickname}`

---

## ⚠ Limitations & Planned Fixes

### 🖱 Discord Feature Temporarily Disabled

- Due to the recent update enabling full headless mode, the Discord feature is temporarily non-functional.
- A future update will restore this feature.

### ✖️ Chrome Restriction

- You **must close all instances of Chrome** using the designated profile before running the script.

---

## 📌 Extra Features

- **Custom AI Names:** Create a group chat with the AI, remove extra members, and rename it. Now you can say:
  ```text
  Hey Meta, send a picture to [Group Name]
  ```

---

## 👨‍💻 Credits

> **Lead Developer:** Cattn

### 💬 Need Help?

- Contact me on Discord: `cattn.`
- For more ways to reach me, visit my [website](https://cattn.dev/).

---