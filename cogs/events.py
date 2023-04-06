import nextcord
from nextcord.ext import commands, tasks
import wavelinkcord as wavelink
import sqlite3

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
                    self.check_member.stop()
                    return


        
    # Listens for a song to end and if the queue is empty it will disconnect the bot
    # Of loop is on it will loop the song
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, i):
        vc: wavelink.Player = i.player
        
        if vc.queue.loop == True:

            await vc.play(i.track)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        query = "INSERT INTO guilds VALUES (?,?)"
        cursor.execute(query, (guild.id, 0))
        database.commit()
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        
        query = "DELETE FROM guilds WHERE guild_id = ?"
        cursor.execute(query, (guild.id,))
        database.commit()

def setup(bot : commands.Bot):
    bot.add_cog(Events(bot))