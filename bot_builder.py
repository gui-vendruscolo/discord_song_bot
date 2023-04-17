import discord 
from discord.ext import commands


def build_bot():
    intents = discord.Intents.all()
    intents.members = True
    return commands.Bot(command_prefix=";", intents=intents)