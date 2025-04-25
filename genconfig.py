import json
import re
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def get_users():
    users = []
    print("Let's add Discord users for direct messaging.")
    print("You'll need their Discord User ID (which you can get by enabling Developer Mode in Discord, right-clicking their name, and selecting 'Copy User ID').")
    while True:
        add_more = input("Add a user? (y/n): ").lower()
        if add_more != 'y':
            break
        name = input("Enter a nickname for the user (e.g., 'Carl', 'John'): ").lower()
        while True:
            user_id_str = input(f"Enter the Discord User ID for {name}: ")
            if user_id_str.isdigit():
                users.append({name: int(user_id_str)})
                break
            else:
                print("Invalid User ID. Please enter only numbers.")
    return users

def get_default_mode():
    cls()
    print("\nSelect the default mode:")
    modes = ["Image", "Text", "Discord"]
    descriptions = [
        "Actively scans for images sent in the chat for AI analysis (Default)",
        "Actively scans for text sent in the chat for AI response.",
        "Actively scans for Discord commands (send message, send image, etc.)"
    ]
    for i, (mode_option, desc) in enumerate(zip(modes, descriptions), 1):
        print(f"{i}. {mode_option} - {desc}")
    while True:
        try:
            choice = int(input("Enter the number for the default mode: "))
            if 1 <= choice <= len(modes):
                return modes[choice - 1].lower()
            else:
                print("Invalid choice. Using default mode 'Image'.")
                return modes[0].lower()
        except ValueError:
            print("Invalid input. Using default mode 'Image'.")
            return modes[0].lower()

def get_default_model():
    cls()
    print("\nSelect the default AI model:")
    models = [
        "chatgpt-4o-latest",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-search-preview-2025-03-11"
    ]
    descriptions = [
        "Latest GPT-4o (Default)",
        "Slightly older, cheaper GPT-4o",
        "Cheap GPT-4o Mini with search (Experimental)"
    ]
    for i, (model_option, desc) in enumerate(zip(models, descriptions), 1):
        print(f"{i}. {model_option} - {desc}")
    while True:
        try:
            choice = int(input("Enter the number for the default model: "))
            if 1 <= choice <= len(models):
                return models[choice - 1]
            else:
                return models[0]
        except ValueError:
            print("Invalid input. Using default model 'chatgpt-4o-latest'.")
            return models[0]

def get_chrome_profile():
    cls()
    print("\nEnter the Chrome profile number you want to use.")
    print("You can find this by navigating to chrome://version in Chrome and looking for 'Profile Path'. The number is usually at the end (e.g., 'Profile 3').")
    print("Ensure that you are logged in to messenger on this profile.")

    while True:
        profile = input("Enter the profile number (e.g., '3'): ")
        if profile.isdigit():
            return profile
        else:
            print("Invalid input. Please enter only the number.")

def get_messenger_link():
    cls()
    print("\nEnter your Messenger group chat/dm link.")
    print("This looks like 'https://www.messenger.com/t/################'.")
    while True:
        link = input("Enter the Messenger link: ")
        if re.match(r"^https://www\.messenger\.com/t/\d+$", link):
            return link
        else:
            print("Invalid format. Please ensure it starts with 'https://www.messenger.com/t/' followed by numbers.")

def main():
    cls()
    print("--- Meta Vision Glasses Configuration ---")

    config_data = {}
    config_data["users"] = get_users()
    config_data["default_mode"] = get_default_mode()
    config_data["default_model"] = get_default_model()
    config_data["chrome_profile"] = get_chrome_profile()
    config_data["messenger_link"] = get_messenger_link()

    try:
        with open("config.json", "w") as f:
            json.dump(config_data, f, indent=4)
        print("\nConfiguration successfully saved to config.json!")
    except IOError as e:
        print(f"\nError saving configuration file: {e}")

if __name__ == "__main__":
    main()
