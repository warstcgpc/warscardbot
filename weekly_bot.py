import os
import random
import requests
from datetime import datetime
import traceback

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

IMAGE_FILE = "image_urls.txt"
POSTED_FILE = "posted_images.txt"

THREAD_MESSAGE = "Here's our card of the week — use this thread to discuss!"

DEBUG = True

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

def discord_request(method, url, payload=None):
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    debug_print(method, url, "Payload:", payload)

    r = requests.request(method, url, headers=headers, json=payload)
    debug_print("Response:", r.status_code, r.text)

    # Handle rate limits
    if r.status_code == 429:
        retry = r.json().get("retry_after", 1)
        raise Exception(f"Rate limited by Discord. Retry after {retry} seconds.")

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

def preflight_check():
    if not BOT_TOKEN or not CHANNEL_ID:
        raise ValueError("Missing BOT_TOKEN or CHANNEL_ID environment variables.")

    # Check bot identity
    me = discord_request("GET", "https://discord.com/api/v10/users/@me")
    print(f"Authenticated as {me.get('username')}#{me.get('discriminator')}")

    # Check channel access
    channel = discord_request("GET", f"https://discord.com/api/v10/channels/{CHANNEL_ID}")
    print(f"Found channel: {channel.get('name')} (type: {channel.get('type')})")

    # Permissions cannot be fully checked via REST for bots
    print("Ensure the bot has: Send Messages + Create Public Threads permissions.")

def main():
    preflight_check()

    all_images = load_image_urls()
    posted_images = load_posted_images()

    unused = [img for img in all_images if img not in posted_images]

    if not unused:
        print("All images used — resetting history.")
        unused = all_images
        open(POSTED_FILE, "w").close()

    image_url = random.choice(unused)

    # Post weekly image
    message = discord_request(
        "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        {"content": f"Weekly Image:\n{image_url}"}
    )
    print(f"Posted image: {image_url}")

    # Create thread
    thread = discord_request(
        "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{message['id']}/threads",
        {
            "name": f"Weekly Image - {datetime.utcnow().strftime('%Y-%m-%d')}",
            "auto_archive_duration": 10080
        }
    )
    print(f"Created thread: {thread['name']}")

    # Post thread starter message
    discord_request(
        "POST",
        f"https://discord.com/api/v10/channels/{thread['id']}/messages",
        {"content": THREAD_MESSAGE}
    )
    print("Posted discussion message in thread.")

    save_posted_image(image_url)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        exit(1)
