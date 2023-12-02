import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelink
#from wavelink.ext import spotify
import random
import sqlite3
import os
DISCORD_TOKEN = "YOUR DISCORD TOKEN HERE"

database = sqlite3.connect('database.db')   #I dont know how any of the db sh*T works
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS dj (guild_id INTEGER, dj_id INTEGER)")
database.execute("CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER, dj_mode BOOLEAN, shuffle BOOLEAN)")

bot_version = "1.0.0"

intents = nextcord.Intents.all()
client = nextcord.Client()
bot = commands.Bot(command_prefix=".", intents=intents)

# TO DO LIST
# 
# - Adding filters to the bot

# - Looping queues not just songs  --Somehow works
# - Vote skipping perhaps

# All the cogs that will be loaded
extensions = [
    'cogs.botcmd',
    'cogs.events',
    'cogs.play',
    'cogs.queue',
    'cogs.dj',
    'cogs.filters',
    'cogs.skip',
        ]

if __name__ == "__main__":
    for ext in extensions:
            print(f"Loading {ext}")
            bot.load_extension(ext)

# Just a list of songs to appear in the bot's status
songs = [
    "\"DIE LIEBE KOMMT NICHT AUS BERLIN - B3k\"",
    "\"Without Me - Eminem\"",
    "\"Nyan Cat for 100 Hours\"",
    "\"CRASH DUMMY (Prod. by SIRA) - BHZ\"",
    "\"Ski Aggu – Party Sahne\"",
    "\"MilleniumKid x JBS – Vielleicht Vielleicht\"",
]

# When the bot is ready, it will create a task to connect to the LavaLink Host
@bot.event
async def on_ready():
    print("Bot Ready!")
    bot.loop.create_task(on_node())
    guild_count = 0
    for guild in bot.guilds:   #shows in the terminal in how many and what servers the bot is
		# PRINT THE SERVER'S ID AND NAME.
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=f"{songs[random.randint(0, 5)]}"))

# This function joins a LavaLink Host
async def on_node():
    #sc = spotify.SpotifyClient(      #i dont like or use Spotify api so i removed it
      #      client_id='ae86a2b160874edf9dbb6b69995b74a8',
        #    client_secret='d470e67805824350b4c778554ed89a12'
      #  )
    node: wavelink.Node = wavelink.Node(uri="http://localhost:2333/", password="youshallnotpass") 
    await wavelink.NodePool.connect(client=bot, nodes=[node])#, spotify=sc
    wavelink.Player.autoplay = True 

bot.run(DISCORD_TOKEN)
#bot.run(os.environ[DISCORD_TOKEN])