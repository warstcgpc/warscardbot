import os
import random
import discord

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

IMAGE_FILE = "image_urls.txt"
POSTED_FILE = "posted_images.txt"

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def load_list(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def save_list(path, items):
    with open(path, "w") as f:
        f.write("\n".join(items))


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # Load image lists
    all_images = load_list(IMAGE_FILE)
    posted_images = load_list(POSTED_FILE)

    # Determine available images
    remaining = [url for url in all_images if url not in posted_images]

    # If no images remain, reshuffle
    if not remaining:
        print("All images used — reshuffling.")
        posted_images = []
        remaining = all_images[:]  # reset to full list
        save_list(POSTED_FILE, posted_images)

