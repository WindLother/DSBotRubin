import sqlite3
import io
from discord.ext import commands
import discord
from bs4 import BeautifulSoup
import httpx

@commands.command(name='character', aliases=['charz', 'char'])
async def character_info(ctx, *, character_name):
    character_name = character_name.replace(" ", "+")
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://rubinot.com/?characters/{character_name}')
    soup = BeautifulSoup(response.text, 'html.parser')

    # Pegando as informações do Character Information
    char_info_divs = soup.find_all('div', {'class': 'TableContainer'})
    char_info_table = char_info_divs[0].find('table', {'class': 'TableContent'})

    if char_info_table is not None:
        char_info = {}
        for row in char_info_table.findAll('tr', {'bgcolor': ['#F1E0C6', '#D4C0A1']}):
            columns = row.findAll('td')
            char_info[columns[0].text.strip().replace(':', '')] = columns[1].text.strip()
    else:
        char_info = {"Error": "Não foi possível encontrar informações deste player."}

    # Pegando as informações do Character Deaths
    char_deaths = []
    if len(char_info_divs) > 1:  # se existe mais de um TableContainer, o segundo deve ser o Character Deaths
        char_deaths_table = char_info_divs[1].find('table')
        for row in char_deaths_table.findAll('tr', {'bgcolor': ['#F1E0C6', '#D4C0A1']}):
            columns = row.findAll('td')
            if len(columns) >= 2:
                char_deaths.append({
                    "Date": columns[0].text.strip(),
                    "Description": columns[1].text.strip(),
                })

    # Enviando as informações do personagem como uma mensagem embutida no Discord
    embed = discord.Embed(
        title=f"Informações para {character_name.replace('+', ' ')}",
        description=f"Aqui estão os detalhes das informações do player `{character_name.replace('+', ' ')}`.",
        color=discord.Color.blue()
    )

    char_info_text = f"**Name**: {char_info.get('Name', '')}\n**Sex**: {char_info.get('Sex', '')}\n**Vocation**: {char_info.get('Vocation', '')}\n**Level**: {char_info.get('Level', '')}\n**Residence**: {char_info.get('Residence', '')}\n**Last login**: {char_info.get('Last login', '')}\n**Account status**: {char_info.get('Account status', '')}"

    death_info_text = ""
    for i, death in enumerate(char_deaths, start=1):
        death_info_text += f"**Death #{i}**\nDate: {death['Date']}\n{death['Description']}\n"

    embed.add_field(name="Character Information", value=char_info_text, inline=False)
    embed.add_field(name="Death Information", value=death_info_text, inline=False)

    await ctx.send(embed=embed)


@commands.command(name='achievement', aliases=['achiev', 'achievements'])
async def achievement(ctx, *, name: str):
    conn = sqlite3.connect('tibiawiki.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    achievement = c.execute("SELECT * FROM achievement WHERE name=?", (name,)).fetchone()
    if achievement is None:
        await ctx.send("Achievement not found.")
    else:
        await ctx.send(f"Achievement: {achievement['name']}\nDescription: {achievement['description']}")


@commands.command(name='monster', aliases=['mob', 'creature'])
async def monster(ctx, *, name: str):
    conn = sqlite3.connect('tibiawiki.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    monster = c.execute("SELECT * FROM creature WHERE name=?", (name,)).fetchone()
    if monster is None:
        await ctx.send("Monster not found.")
    else:
        embed = discord.Embed(title=monster['name'], description=monster['title'])
        embed.add_field(name="Hitpoints", value=monster['hitpoints'])
        embed.add_field(name="Experience", value=monster['experience'])
        embed.add_field(name="Armor", value=monster['armor'])
        embed.add_field(name="Speed", value=monster['speed'])
        embed.add_field(name="Creature Class", value=monster['creature_class'])
        embed.add_field(name="Creature Type", value=monster['creature_type'])
        embed.add_field(name="Location", value=monster['location'])
        # Só add os outros campos se precisar

        if monster['image']:
            file = discord.File(io.BytesIO(monster['image']), filename="image.gif")
            embed.set_image(url="attachment://image.gif")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)


@monster.error
async def monster_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify a monster name.')
    else:
        await ctx.send(f'An error occurred: {error}')


@commands.command(name='spell')
async def spell(ctx, *, name: str):
    conn = sqlite3.connect('tibiawiki.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    spell = c.execute("SELECT * FROM spell WHERE name=?", (name,)).fetchone()
    if spell is None:
        await ctx.send("Spell not found.")
    else:
        embed = discord.Embed(title=spell['name'], description=spell['effect'])
        embed.add_field(name="Words", value=spell['words'])
        embed.add_field(name="Type", value=spell['type'])
        embed.add_field(name="Level", value=spell['level'])
        embed.add_field(name="Mana", value=spell['mana'])
        embed.add_field(name="Soul", value=spell['soul'])
        embed.add_field(name="Price", value=spell['price'])
        embed.add_field(name="Cooldown", value=spell['cooldown'])
        '''embed.add_field(name="Knight", value=spell['knight'])
        embed.add_field(name="Sorcerer", value=spell['sorcerer'])
        embed.add_field(name="Druid", value=spell['druid'])
        embed.add_field(name="Paladin", value=spell['paladin'])'''
        # Add more fields as needed

        # Add image if it exists
        if spell['image']:
            file = discord.File(io.BytesIO(spell['image']), filename="image.gif")
            embed.set_image(url="attachment://image.gif")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)


@spell.error
async def spell_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify a spell name.')
    else:
        await ctx.send(f'An error occurred: {error}')


@commands.command(name='item')
async def item(ctx, *, name: str):
    conn = sqlite3.connect('tibiawiki.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    item = c.execute("SELECT * FROM item WHERE name=?", (name,)).fetchone()
    if item is None:
        await ctx.send("Item not found.")
    else:
        embed = discord.Embed(title=item['name'], description=item['title'])
        embed.add_field(name="Value Sell", value=item['value_sell'])
        embed.add_field(name="Item Class", value=item['item_class'])
        embed.add_field(name="Item Type", value=item['item_type'])
        # Add more fields as needed

        # Fetch item attributes
        attributes = c.execute("SELECT * FROM item_attribute WHERE item_id=?", (item['article_id'],)).fetchall()
        for attr in attributes:
            embed.add_field(name=attr['name'], value=attr['value'])

        # Add image if it exists
        if item['image']:
            file = discord.File(io.BytesIO(item['image']), filename="image.gif")
            embed.set_image(url="attachment://image.gif")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)


@item.error
async def item_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify an item name.')
    else:
        await ctx.send(f'An error occurred: {error}')


@commands.command(name='charm', aliases=['charms'])
async def charm(ctx, *, name: str = None):
    conn = sqlite3.connect('tibiawiki.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if name is None:
        charms = c.execute("SELECT name FROM charm").fetchall()
        await ctx.send("Here are all the charms:\n" + "\n".join([charm['name'] for charm in charms]))
    else:
        charm = c.execute("SELECT * FROM charm WHERE name=?", (name,)).fetchone()
        if charm is None:
            await ctx.send("Charm not found.")
        else:
            embed = discord.Embed(title=charm['name'], description=charm['effect'])
            embed.add_field(name="Type", value=charm['type'])
            embed.add_field(name="Cost", value=charm['cost'])
            # Add more fields as needed

            # Add image if it exists
            if charm['image']:
                file = discord.File(io.BytesIO(charm['image']), filename="image.gif")
                embed.set_image(url="attachment://image.gif")
                await ctx.send(file=file, embed=embed)
            else:
                await ctx.send(embed=embed)


@charm.error
async def charm_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify a charm name.')
    else:
        await ctx.send(f'An error occurred: {error}')


@commands.command(name='imbuement')
async def imbuement(ctx, *, name: str):
    conn = sqlite3.connect('tibiawiki.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    name = name.lower()  # convert user input to lowercase
    imbuement = c.execute("SELECT * FROM imbuement WHERE LOWER(name)=?",
                          (name,)).fetchone()  # convert database value to lowercase
    if imbuement is None:
        await ctx.send("Imbuement not found.")
    else:
        embed = discord.Embed(title=imbuement['name'], description=imbuement['effect'])
        embed.add_field(name="Tier", value=imbuement['tier'])
        embed.add_field(name="Type", value=imbuement['type'])
        embed.add_field(name="Category", value=imbuement['category'])
        embed.add_field(name="Slots", value=imbuement['slots'])
        # Add more fields as needed

        # Add image if it exists
        if imbuement['image']:
            file = discord.File(io.BytesIO(imbuement['image']), filename="image.gif")
            embed.set_image(url="attachment://image.gif")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)


@imbuement.error
async def imbuement_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify an imbuement name.')
    else:
        await ctx.send(f'An error occurred: {error}')