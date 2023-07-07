import os
import discord
from discord.ext import commands
from commands import character_info, achievement, monster, monster_error, spell, spell_error, item, item_error, charm, charm_error, imbuement, imbuement_error
from datascrap import start_checking_deaths
from events import event_commands, list_events
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="+", intents=intents)

bot.add_command(achievement)
bot.add_command(monster)
bot.add_command(spell)
bot.add_command(item)
bot.add_command(charm)
bot.add_command(imbuement)
bot.add_command(character_info)
bot.add_command(list_events)

@bot.event
async def on_ready():
    print(f'{bot.user.name} se conectou ao Discord!')
    start_checking_deaths(bot)  # passar o bot como argumento
    event_commands(bot, 1125417003381969048)

discord_key = os.getenv('DISCORD_KEY')
bot.run(discord_key)
