import os
import logging
import json
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.tree.command(name="embed", description="Parse JSON and post message with embeds")
@app_commands.describe(embed_json="Raw JSON string for the message payload")
async def embed_command(interaction: discord.Interaction, embed_json: str):
    try:
        data = json.loads(embed_json)
        
        content = data.get('content')
        
        embeds = []
        if 'embeds' in data:
            embeds = [discord.Embed.from_dict(e) for e in data['embeds']]
        elif any(k in data for k in ('title', 'description', 'fields', 'color')):
            embeds = [discord.Embed.from_dict(data)]

        if not content and not embeds:
            await interaction.response.send_message("JSON must contain 'content' or 'embeds'.", ephemeral=True)
            return

        # Discord allows up to 10 embeds per message
        await interaction.response.send_message(content=content, embeds=embeds[:10])
        
    except json.JSONDecodeError:
        await interaction.response.send_message("Error: Invalid JSON format.", ephemeral=True)
    except Exception as e:
        logging.error(f"Embed error: {e}")
        await interaction.response.send_message(f"Error parsing data: {e}", ephemeral=True)

if __name__ == '__main__':
    if not TOKEN:
        logging.error("DISCORD_TOKEN not found in .env file")
    else:
        bot.run(TOKEN)