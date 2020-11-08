import discord
import random

info =  "The Discord Bot Maexchen is offering commands to roll dices for the known game (Mia in English).\n"
info += "Type 'r' for rolling the dices. Result is just shown to user who entered the command.\n"
info += "Anyone can enter 's' for showing the last result for all in the channel.\n"
info += "'h' will show this info message in the channel.\n"

class Dices:

    value = "no dices rolled yet"  # values of the last roll

    def __init__(self):
        random.seed(a=None)
        print("Random generator seeded with system time.")

    def roll(self):
        self.value = random.choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"])
        self.value += " "
        self.value += random.choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"])
        return self.value


print("Starting bot...")

TOKEN = open("token.txt", "r").readline()
client = discord.Client()
dices = Dices()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "h":
        await message.channel.send(info)

    if message.content == 'r':
        await message.author.send(dices.roll())

    if message.content == 's':
        await message.channel.send(dices.value)

print("Bot is ready!")
client.run(TOKEN)
