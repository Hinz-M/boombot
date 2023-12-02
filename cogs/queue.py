import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelinkcord
import cogs.embeds as embeds
#from wavelink.ext import spotify
from cogs.dj import djCommands as dj


class queueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Creates a subcommand for the queue command
    @nextcord.slash_command()
    async def queue(self, interaction : nextcord.Interaction):

        pass
    
    # Shows the current queue by copying the queue and then adding each song to an embed
    @queue.subcommand(description="Shows the current Queue")
    async def show(self, interaction : nextcord.Interaction):
        vc: wavelinkcord.Player = interaction.guild.voice_client
        if not vc.queue.is_empty:
            em = nextcord.Embed(title="Queue") 
            em.add_field(name=f"Now Playing", value=f"{vc.current.title}", inline=False)
            queue = vc.queue.copy()
            songs = []
            song_count = 0
            for song in queue:
                song_count += 1
                songs.append(song)
                if song_count == 1:
                    em.add_field(name=f"Up Next", value=f"`[{song_count}]` {song.title}", inline=False)
                
                else:

                    em.add_field(name="", value=f"`[{song_count}]` {song.title} [{round((song.duration / 1000) / 60, 2)}]", inline=False)

            await interaction.response.send_message(embed=em)
        else:
            await interaction.response.send_message("Queue is empty!")

    # Clears the queue using the clear method
    @queue.subcommand(description="Clears the Queue")
    async def clear(self, interaction : nextcord.Interaction):  #this command doesnt work
        #async def clear():
            vc: wavelinkcord.Player = interaction.guild.voice_client
            vc.queue._queue.clear()
            await interaction.response.send_message("The Queue Has Been Cleared")
        
       # await dj.djCheck(self, interaction, clear)
    
    # Removes a song from the queue
    @queue.subcommand(description="Removes a specific song from the queue")
    async def remove(self, interaction: nextcord.Interaction, position: int):
      #async def remove():
        vc: wavelinkcord.Player = interaction.guild.voice_client

        if position < 1 or position > len(vc.queue):
            await interaction.response.send_message("Invalid position. Please provide a valid position in the queue.")
            return

        queue = list(vc.queue)

        try:
            removed_song = queue.pop(position - 1)
            await interaction.response.send_message(f"Successfully removed {removed_song.title} {removed_song.uri}!")
        except IndexError:
            await interaction.response.send_message("Song not found in queue!")

        vc.queue._queue = queue

        if not vc.is_playing():
            if len(vc.queue) > 0:
                next_song = await vc.queue.get()
                await vc.play(next_song)

        #await remove()

    
    # Skips to a specific song in the queue
    @queue.subcommand(description="Removes a specific song from the queue")
    async def skipto(self, interaction: nextcord.Interaction, position: int):
        async def skipto():
            vc: wavelinkcord.Player = interaction.guild.voice_client

            if position < 1 or position > len(vc.queue):
                await interaction.response.send_message("Invalid position. Please provide a valid position in the queue.")
                return

            queue = list(vc.queue)

            # Retrieve the song at the specified position
            song = queue[position - 1]

            # Play the song and remove it from the queue
            await vc.play(song)
            queue.remove(song)

            # Update the queue in the player
            vc.queue._queue = queue

            # Send the appropriate embed based on the song source (YouTube or Spotify)
            if isinstance(song, wavelinkcord.YouTubeTrack):
                embed = embeds.playEmbed(song, vc)
            elif isinstance(song, spotify.SpotifyTrack):
                embed = embeds.whatsPlayingSpotify(song, vc)
            else:
                embed = None

            await interaction.response.send_message(embed=embed)

        await skipto()
    



def setup(bot : commands.Bot):
    bot.add_cog(queueCommands(bot))