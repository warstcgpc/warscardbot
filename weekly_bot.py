import os
import random
import requests
from datetime import datetime

# Environment variables from GitHub Actions secrets
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

# File paths
IMAGE_FILE = "image_urls.txt"
POSTED_FILE = "posted_images.txt"

# Standard thread message
THREAD_MESSAGE = "💬 Here's our card of the week — use this thread to discuss!"

def send_discord_message(url, payload):
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code not in (200, 201):
        raise Exception(f"Discord API Error {r.status_code}: {r.text}")
    return r.json()

def load_image_urls():
    if not os.path.exists(IMAGE_FILE):
        raise FileNotFoundError(f"Image file '{IMAGE_FILE}' not found.")
    with open(IMAGE_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_posted_images():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_posted_image(image_url):
    with open(POSTED_FILE, "a") as f:
        f.write(image_url + "\n")

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        raise ValueError("Missing BOT_TOKEN or CHANNEL_ID environment variables.")

    all_images = load_image_urls()
    posted_images = load_posted_images()

    # Determine unused images
    unused_images = [img for img in all_images if img not in posted_images]

    # Reset if all images have been used
    if not unused_images:
        print("🔄 All images used — resetting history.")
        posted_images = []
        unused_images = all_images
        with open(POSTED_FILE, "w") as f:
            pass  # Clear file

    # Pick a random unused image
    image_url = random.choice(unused_images)

    # Post image in channel
    message_payload = {"content": f"📷 Weekly Image:\n{image_url}"}
    message = send_discord_message(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        message_payload
    )
    print(f"✅ Posted image: {image_url}")

    # Create thread from message
    thread_payload = {
        "name": f"Weekly Image - {datetime.utcnow().strftime('%Y-%m-%d')}",
        "auto_archive_duration": 10080  # 7 days
    }
    thread = send_discord_message(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{message['id']}/threads",
        thread_payload
    )
    print(f"🧵 Created thread: {thread['name']}")

    # Post standard message in thread
    send_discord_message(
        f"https://discord.com/api/v10/channels/{thread['id']}/messages",
        {"content": THREAD_MESSAGE}
    )
    print("📝 Posted discussion message in thread.")

    # Save posted image to history
    save_posted_image(image_url)

if __name__ == "__main__":
    main()
