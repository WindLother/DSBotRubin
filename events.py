import discord
from discord.ext import commands
import aiocron
import datetime
import pytz
from typing import List

tz = pytz.timezone('America/Sao_Paulo')

class Event:
    def __init__(self, name: str, when: str, place: str, image: str, readable_time: str):
        self.name = name
        self.when = when
        self.place = place
        self.image = image
        self.readable_time = readable_time


events = [
    Event('Feroxa', '1 0 13,26 * *', 'Grimvale', 'images/events/feroxa.gif', 'Dia 13 e 26 do mês. O horário varia entre às 3h e 12h.'),
    Event('Feverish Citizens', '0 18 * * 2,4', 'Venore', 'images/events/feverish_citizens.gif', 'Toda terça e quinta-feira às 18:00.'),
    Event('Draptor', '0 19 * * 1,3', 'Zao, Dragonblaze Peaks, Razzachai', 'images/events/draptor.gif', 'Toda segunda e quarta-feira às 19:00.'),
    Event('Midnight Panther', '0 15 * * 2,4', 'Floresta Tiquanda', 'images/events/midnight_panther.gif', 'Toda terça e quinta-feira às 15:00.'),
    Event('Undead Cavebear', '0 23 * * 5,0', 'Lich Hell', 'images/events/undead_cavebear.gif', 'Toda sexta-feira e domingo às 23:00.'),
    Event('Crustacea', '0 18 * * 3,6', 'Calassa, Seacrest Grounds, Treasure Island', 'images/events/crustacea.gif', 'Toda quarta-feira e sábado às 18:00.')
]

async def send_event_message(bot, event: Event, channel_id):
    channel = bot.get_channel(channel_id)  # Envia a mensagem para o canal especificado
    embed = discord.Embed(
        title=f"{event.name} Evento próximo de iniciar!",
        description=f"O {event.name} evento irá iniciar em breve às {event.place}. Esteja pronto!",
        color=discord.Color.blue()
    )
    if event.name == 'Feroxa':
        embed.description = f"O evento {event.name} ocorre hoje! O horário do evento varia entre às 3h e 12h no local {event.place}. Esteja atento!"
    file = discord.File(event.image, filename="event.png")
    embed.set_image(url="attachment://event.png")
    await channel.send(file=file, embed=embed)


def event_commands(bot, channel_id):
    for event in events:
        @aiocron.crontab(event.when, tz=tz)
        async def cronjob():
            now = datetime.datetime.now(tz)
            if now.hour == int(event.when.split()[1]) and now.minute == int(event.when.split()[0]) - 10:
                await send_event_message(bot, event, channel_id)

@commands.command(name='events', aliases=['eventos', 'raid', 'event'])  # Comando para listar todos os eventos
async def list_events(ctx):
    embed = discord.Embed(
        title="Próximos Eventos",
        description="Aqui estão os próximos eventos:",
        color=discord.Color.blue()
    )
    for event in events:
        embed.add_field(name=event.name, value=f"Local: {event.place}\nHorário: {event.readable_time}", inline=False)
    await ctx.send(embed=embed)
