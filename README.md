# Meta Vision Glasses (name pending)
Let your glasses see for you!

## Installation
> It is highly recommended to use a venv.
- ``pip install -r requirements.txt``
- ``playwright install``

## Setup
- Ensure you've setup your openai token as an environment variable (per official docs) OR just add it to main.py under ``api_key=``
- [Optional] Setup your discord friends for quick-access. in the ``user_urls`` object, add all of your friends ids/nicknames. Example below
```json
"cattn": "https://discord.com/channels/@me/111241284124814",
```

### Creating a new Profile for playwright
- Create a new chrome profile for this app. Based on the order of creation/amount of profiles (Profile 1 = first extra created, etc) you will need to change the ``args`` variable to fit that profile. If this is your first new profile, leave it at default.
- In that profile, visit discord.com/app in another tab, and login with whichever account you'd like to use.
- In another tab, login to messenger with whichever account you'd like to use for the bot

### Running
- run ``py main.py``, then simply leave your device on that screen.
- In the future this program will have full headless support so it can run in the background or on a server.

# Usage

## Communicating with ChatGPT
- On the glasses, say "Hey meta, send a picture to [Account Name]"
- Confirm the name
- Then optionally, you can say "Hey meta, read out my message" and it'll read out the response.

## Commands
> To use a command, simply send a message to your account with the command. You can speak all of these commands.
- **Switch Mode**: ``switch mode to {mode}``
- **Send Message** _(only in Discord mode)_: ``send message to {nickname} {message}``
- **Send Image** _(only in Discord mode)_: ``send image to {nickname}``

### Supported Modes:
- Discord
- Image

### Send Image (Discord)
Before sending running the send image command, you need to send an image to chat with Discord mode activated.

Example:
- ``switch mode to discord``
- Send image
- ``send image to {nickname}

## Extra
- If you'd like to have custom names for your AI, then create a group with the AI and one other, remove the other, then rename the group to whatever you'd like. Then you will be able to say "Hey meta, send a picture to [Group Name]".

# Credits
> Lead Developer - Cattn

### Need help?
You can contact me on discord @ ``cattn.``, If you need to reach me some other way, check out my contacts on my [website](https://cattn.dev/)
