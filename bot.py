import os
import random
import discord
from datetime import datetime

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

    # Pick a random unused image
    chosen = random.choice(remaining)

    # Prepare embed
    embed = discord.Embed(
        title="WARS Card of the Week",
        description="Discuss this week's featured card!",
        color=0xFFD700
    )
    embed.set_image(url=chosen)

    # Post embed to channel
    channel = client.get_channel(CHANNEL_ID)
    message = await channel.send(embed=embed)

    # Create a thread under the message
    # Format today's date as yyyy-MM-dd
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    thread = await message.create_thread(
        name=f"Card of the Week {today_str}"
    )

    # Post follow-up message inside the thread
    await thread.send("Here's the WARS Card of the Week - Discuss here!")

    # Record the posted image
    posted_images.append(chosen)
    save_list(POSTED_FILE, posted_images)

    # Close bot so GitHub Actions can finish
    await client.close()


client.run(TOKEN)
