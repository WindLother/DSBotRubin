import httpx
from bs4 import BeautifulSoup
from discord.ext import tasks
import discord

CHANNEL_ID = 1125417003381969048
players_to_watch = {"Olsen",
                    "Seu Boga",
                    "Battouzai",
                    "Seduruk",
                    "Devastada",
                    "Tony Tornado",
                    "Patrone",
                    "Maxo Canadense",
                    "Kid Icarus"}

# Armazenar as últimas N mortes reportadas
N = 10
last_reported_deaths = {player: [("", "")]*N for player in players_to_watch}

def start_checking_deaths(bot):
    @tasks.loop(seconds=60)
    async def check_deaths():
        global last_reported_deaths

        async with httpx.AsyncClient() as client:
            response = await client.get('https://rubinot.com/?lastkills')
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', {'class': 'TableContent'})

        for row in table.findAll('tr', {'bgcolor': ['#F1E0C6', '#D4C0A1']}):
            columns = row.findAll('td')

            death_time = columns[1].text.strip()  # Obtendo a hora da morte
            player_name_column = columns[2]
            player_name = player_name_column.find('a').text

            if player_name in players_to_watch:
                death_info = " ".join(player_name_column.text.split())  # Limpeza do death_info

                # Verificar se a morte já foi reportada
                if (death_info, death_time) not in last_reported_deaths[player_name]:
                    print(f"Player name: {player_name}")
                    print(f"Death info: {death_info}")
                    print(f"Death time: {death_time}")

                    channel = bot.get_channel(CHANNEL_ID)
                    # Cria uma nova mensagem embutida
                    embed = discord.Embed(
                        title=f":skull: {player_name} morreu!",
                        description=f"{death_info} às {death_time}",
                        color=discord.Color.dark_red()
                    )
                    await channel.send(embed=embed)
                    # Agora nós atualizamos a última morte reportada
                    last_reported_deaths[player_name].pop(0)
                    last_reported_deaths[player_name].append((death_info, death_time))

    print(last_reported_deaths)
    check_deaths.start()
