import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelink
from cogs.dj import djCommands as dj


class skipCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Skips the current song by stopping it and then "on_wavelink_track_end" starts the next song
    # Wont skip the song if either the queue is empty or if loop is on
    @nextcord.slash_command(description="Skip the current song")
    async def skip(self, interaction : nextcord.Interaction):

        #async def skip():
            #listeners = len(interaction.guild.voice_client.channel.members) - 1

            vc: wavelink.Player = interaction.guild.voice_client
            await vc.stop()
            if not vc.queue.is_empty:

                    await vc.stop()
                    await interaction.response.send_message("Song skipped!")
                
            elif vc.queue.loop == True:    #this does work, but its buggy and if the queue is too long, the last songs dont get looped 

                    await interaction.response.send_message("Turn off looping to skip!")
            else:

                    await interaction.response.send_message("Cant Skip! There is nothing in the Queue")
            

        #await dj.djCheck(self, interaction, skip)
    

def setup(bot : commands.Bot):
    bot.add_cog(skipCommands(bot))