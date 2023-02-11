import asyncio
import math
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import pandas as pd

import contract
import player as p

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

global offers_made
offers_made = []

global accept_offers
accept_offers = False

global cur_player


@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))


@client.command()
async def stop(ctx):
    if str(ctx.message.author) != "Huardy#9391":
        await ctx.channel.send("Sorry, your team isn't good enough to stop free agency!")
        return ""
    await ctx.channel.send("Congratulations everyone, free agency signings are now complete.\n"
                           "Good luck!")


@client.command()
async def start(ctx):
    if str(ctx.message.author) != "Huardy#9391":
        await ctx.channel.send("Sorry, your team isn't good enough to start free agency!")
        return ""

    player_list = pd.read_csv("players.txt", sep="\t")
    global cur_player

    def check(mes):
        return mes.content == "!spin"

    for i, player in player_list.iterrows():
        global offers_made
        offers_made = []
        cur_player = p.Player(player["First Name"], player["Last Name"], player["Position"],
                                   player["College"], player["Rating"], player["Potential"],
                                   player["Personality"], player["Age"], player["Former Team"], "", "")
        await auction_player(ctx, cur_player)
        await client.wait_for("message", check=check)
        await asyncio.sleep(4)

    await ctx.channel.send("Congratulations everyone, free agency signings are now complete.\n"
                           "Good luck!")


async def auction_player(ctx, cur_player):
    await print_player_info(ctx, cur_player)


async def print_player_info(ctx, cur_player):
    global accept_offers
    accept_offers = True

    if cur_player.age <= 28:
        cur_player.timeframe = "Progression"
    elif 29 <= cur_player.age <= 32:
        cur_player.timeframe = "Regression"
    else:
        cur_player.timeframe = "Regression"

    embed = discord.Embed(title="Now accepting offers for:")
    embed.add_field(name="Player", value=cur_player.pos + " " + cur_player.first_name + " " + cur_player.last_name, inline=False)
    embed.add_field(name="College", value=cur_player.college, inline=False)
    embed.add_field(name="Age", value=f"{cur_player.age}, {cur_player.timeframe}", inline=False)
    embed.add_field(name="Rating", value=f"{cur_player.rating} ({cur_player.potential})", inline=False)
    embed.add_field(name="Personality", value=f"{cur_player.trait}", inline=False)
    embed.add_field(name="Former Team", value=f"{cur_player.former_team}", inline=False)

    react = await ctx.send(embed=embed)
    await react.add_reaction("✅")


@client.command()
async def remove(ctx):
    message = str(ctx.message.content)
    message = message.split(" ", 1)
    print(message)

    for i, current_offer in enumerate(offers_made):
        if message[1] == current_offer.user:
            await ctx.channel.send("Offer successfully removed.")
            offers_made.remove(offers_made[i])
            break

@client.command()
@commands.check(lambda x: accept_offers)
async def offer(ctx):
    # $m/#y - 5m/3y
    # !offer 5/3
    # Gets message from user without the command
    message = str(ctx.message.content)
    message = message.split(" ")[1]

    user = str(ctx.author).split("#")[0]
    try:
        money = message.split("/")[0]
        length = message.split("/")[1]
    except IndexError:
        await ctx.channel.send("Please enter your offer in the valid format: $/y")
        return ""

    try:
        if int(length) > 5:
            raise InvalidContractLengthException
    except InvalidContractLengthException:
        await ctx.channel.send("Contracts can be no longer than 5 years.")
        return ""

    new_offer = contract.Contract(user, int(money), int(length), 0)
    entries = calculate_entries(new_offer.yearly_price, cur_player.age, new_offer.length)
    new_offer.entries = entries

    if new_offer.user == "GriffKip":
        new_offer.user = "St. Louis Knights"
    elif new_offer.user == "Huardy":
        new_offer.user = "San Antonio Cannons"
    elif new_offer.user == "BigMoneyBrady":
        new_offer.user = "Oklahoma Bison"
    elif new_offer.user == "c_garrett09":
        new_offer.user = "Alabama Racers"
    elif new_offer.user == "HutchD":
        new_offer.user = "Memphis Rhythm"
    elif new_offer.user == "TJames":
        new_offer.user = "Kentucky Cluck"

    # TODO: Check that new_offer > current_offer (maybe)
    # Adds new offers to offers_made and allows updating offers from the same user
    for i, current_offer in enumerate(offers_made):
        if new_offer.user == current_offer.user:
            offers_made.remove(offers_made[i])
            break

    offers_made.append(new_offer)

    embed_offer = f"The {new_offer.user} has offered ${new_offer.yearly_price},000,000 for {new_offer.length} years for {cur_player.first_name} {cur_player.last_name}.\n" \
                  f"They now have {math.trunc(entries)} entries."
    await ctx.channel.send(embed_offer)


# Andrew Brady
def calculate_entries(m, a, p):
    # Define age categories and their multipliers
    progression, prime, regression = [3, 2.5, 2, 1.5, 1], [2, 2.5, 3, 2.5, 2], [1, 1.5, 2, 2.5, 3]

    if a <= 27:
        entries = (m * progression[p - 1] * 2)
    elif a <= 32:
        entries = (m * prime[p - 1] * 2)
    else:
        entries = (m * regression[p - 1] * 2)

    return entries


@client.command(name="spin")
async def choose_winner(ctx):

    if str(ctx.message.author) != "Huardy#9391":
        await ctx.channel.send("Sorry, your team isn't good enough to spin the wheel!")
        return ""

    import time
    import random
    winner = random.choices(offers_made, weights=(cur.entries for cur in offers_made))

    embed = discord.Embed(title=f"{cur_player.first_name} {cur_player.last_name} has signed with:")
    embed.add_field(name="Team", value=winner[0].user)
    embed.add_field(name="Yearly Salary", value=f"${winner[0].yearly_price},000,000")
    embed.add_field(name="Length", value=f"{winner[0].length} years")

    await ctx.channel.send("The winner is...")
    time.sleep(2)
    await ctx.channel.send(embed=embed)


class InvalidContractLengthException(Exception):
    pass;

client.run(TOKEN)
