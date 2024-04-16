import nextcord
from nextcord.ext import commands, tasks
import wavelinkcord as wavelinkcord
import sqlite3
import random
from nextcord.ext import application_checks
import cogs.radio as radio
database = sqlite3.connect('database.db')
cursor = database.cursor()


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_member.start()
    
    # Checks if the bot is alone in a voice channel and if it is it will disconnect every 10 seconds
    @tasks.loop(seconds=10)
    async def check_member(self):  

        for vc in self.bot.voice_clients:
            if len(vc.channel.members) == 1:
                if vc.channel.members[0].id == self.bot.user.id:
                    await vc.disconnect()


        
    # Listens for a song to end and if the queue is empty it will disconnect the bot
    # Of loop is on it will loop the song
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, i):

        vc: wavelinkcord.Player = i.player
        query = "SELECT shuffle FROM guilds WHERE guild_id = ?"
        loop = cursor.execute(query, (vc.guild.id,)).fetchone()

        # Checks if shuffling is enabled and if so, random.choice a song frm the queue and then remove it.
        # Had to disable auto play because it would send the bot into a loop

        if loop[0] == 1: # If shuffle enabled

            queue = vc.queue.copy()
            queue = list(queue)

            choice = random.choice(queue)
            queue.remove(choice)

            await vc.play(choice, populate=True)
            vc.queue.clear()

            for song in queue:
                await vc.queue.put_wait(song)

        elif vc.queue.loop == False and not vc.queue.is_empty: # Play next song in queue

            populate = len(vc.auto_queue) < vc._auto_threshold
            await vc.play(vc.queue.get(), populate=populate)

        elif vc.queue.loop == True:
             # If loop is on
            await vc.play(i.track)
        elif not vc.is_playing():
            await self.bot.get_cog('radioCommands').play_radio(vc) #.guild_id
            #await self.bot.get_cog('radioCommands').play_radio(vc) #.guild_id
       
            
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        query = "INSERT INTO guilds VALUES (?,?,?)"
        cursor.execute(query, (guild.id, 0, 0))
        database.commit()
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        
        query = "DELETE FROM guilds WHERE guild_id = ?"
        cursor.execute(query, (guild.id,))
        database.commit()

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):

        if isinstance(error, application_checks.ApplicationMissingPermissions):
            await ctx.send(f"`Error` : {error}")
        
    
    @nextcord.slash_command()
    async def autoplay(self, interaction):

        vc : wavelinkcord.Player = interaction.guild.voice_client
        print(vc.autoplay)

def setup(bot : commands.Bot):
    bot.add_cog(Events(bot))