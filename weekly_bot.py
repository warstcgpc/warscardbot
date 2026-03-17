import os
import random
import requests
from datetime import datetime
import traceback

# Environment variables from GitHub Actions secrets
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

# File paths
IMAGE_FILE = "image_urls.txt"
POSTED_FILE = "posted_images.txt"

# Standard thread message
THREAD_MESSAGE = "💬 Here's our card of the week — use this thread to discuss!"

DEBUG = True  # Set to True to print extra info

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

def send_discord_message(url, payload):
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    debug_print("POST", url, "Payload:", payload)
    r = requests.post(url, headers=headers, json=payload)
    debug_print("Response Code:", r.status_code)
    debug_print("Response Body:", r.text)
    if r.status_code not in (200, 201):
        raise Exception(f"Discord API Error {r.status_code}: {r.text}")
    return r.json()

def load_image_urls():
    if not os.path.exists(IMAGE_FILE):
        raise FileNotFoundError(f"Image file '{IMAGE_FILE}' not found.")
    with open(IMAGE_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    if not urls:
        raise ValueError("No image URLs found in image_urls.txt")
    return urls

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

    unused_images = [img for img in all_images if img not in posted_images]

    if not unused_images:
        print("🔄 All images used — resetting history.")
        posted_images = []
        unused_images = all_images
        with open(POSTED_FILE, "w") as f:
            pass

    image_url = random.choice(unused_images)

    message_payload = {"content": f"📷 Weekly Image:\n{image_url}"}
    message = send_discord_message(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        message_payload
    )
    print(f"✅ Posted image: {image_url}")

    thread_payload = {
        "name": f"Weekly Image - {datetime.utcnow().strftime('%Y-%m-%d')}",
        "auto_archive_duration": 10080
    }
    thread = send_discord_message(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{message['id']}/threads",
        thread_payload
    )
    print(f"🧵 Created thread: {thread['name']}")

    send_discord_message(
        f"https://discord.com/api/v10/channels/{thread['id']}/messages",
        {"content": THREAD_MESSAGE}
    )
    print("📝 Posted discussion message in thread.")

    save_posted_image(image_url)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ ERROR:", e)
        traceback.print_exc()
        exit(1)
