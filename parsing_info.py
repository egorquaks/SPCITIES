import asyncio
import os

import discord
from dotenv import load_dotenv

from utils import get_name

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

GUILD_ID = 421745054110187520

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


async def get_members():
    members_id = []
    await client.login(BOT_TOKEN)
    guild = await client.fetch_guild(GUILD_ID)
    async for member in guild.fetch_members():
        members_id.append(member.id)
    await client.close()
    return members_id


if __name__ == '__main__':
    members = asyncio.run(get_members())
    print(members)

    for i in members:
        print(get_name(str(i)))
