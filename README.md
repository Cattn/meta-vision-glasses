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

## 🛠 Setup

### 1️⃣ API Keys

Create a `.env` file in the root directory and add your OpenAI API key and Gemini API key:

```env
API_KEY="YOUR_OPENAI_API_KEY"
GEM_KEY="YOUR_GEMINI_API_KEY"
```

The program will automatically load these keys from the `.env` file.

### 2️⃣ Creating a New Chrome Profile for Playwright

1. Create a new Chrome profile dedicated to this application.
2. Log in to Discord via [discord.com/app](https://discord.com/app) with your desired account.
3. Log in to Messenger with the desired account for the program.

### 3️⃣ Configuration File

Run ``genconfig.py`` to generate a config based on a series of questions.

## 🏃 Running the Program

Start the program using:

```sh
py main.py
```

> There won't be much useful output in the terminal.

---

## 📢 Usage

### 🎧 Interfacing with the AI/Bot
   - Say: *"Hey Meta, send a picture to [Account Name]"*.
   - Confirm the name.
   - Optionally, say: *"Hey Meta, read out my message"* to hear the response.

### 🎤 Voice Notes (Audio Mode)
   - Say: *"Hey Meta, send a voice note to [Account Name]"*.
   - Confirm the name.
   - Optionally, say: *"Hey Meta, read out my message"* to hear the response.

**Note:**

- Any voice note sent (regardless of mode) will be processed by the preset model: `gpt-4o-mini-audio-preview-2024-12-17`.
- This model **cannot** be changed at this time.

### 🎥 Videos (Video Mode)

- Any video sent will be automatically processed using `gemini-2.5-pro-exp-03-25`.
- Ensure `GEM_KEY` is added to your `.env` file for this feature to function properly.
- The AI will generate insights, summaries, or descriptions based on the video content.


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

1. Say: *"Hey Meta, send a message to [Account Name]"*.
2. Say: *"switch mode to discord"*.
3. Say: *"Hey meta, send an image to [Account Name]"*.
4. Say: *"Hey Meta, send a message to [Account Name]"*.
5. Say: *"send image to [User]"*.

> Unfortunately, there isn't much I can do to shorten this workflow. You can however, just take the photo with your glasses, and send it by typing the commands. The ability to use your voice for the commands is intended for users who need full autonomy from their phone when using this program.


## ⚠ Limitations & Planned Fixes

### 🖱 Discord Feature Temporarily Disabled

- Due to the recent update enabling full headless mode, the Discord feature is temporarily non-functional.
- A future update will restore this feature.

### ✖️ Chrome Restriction

- You **must close all instances of Chrome** before running the script. You can however use other browsers.


## 📌 Extra Info

- **Custom AI Names:** Create a group chat with your bot account, remove extra members, and rename it. Now you can say:
  ```text
  Hey Meta, send a picture to [Group Name]
  ```

## 👨‍💻 Credits

> **Lead Developer:** Cattn

### 💬 Need Help?

- Contact me on Discord: `cattn.`
- For more ways to reach me, visit my [website](https://cattn.dev/).

---
