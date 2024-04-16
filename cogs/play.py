import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelink
#from wavelink.ext import spotify
import cogs.embeds as embeds


import sqlite3
import re
import os
import shutil
import random
import requests
#from bs4 import BeautifulSoup
#from cogs.dj import djCommands as dj

database = sqlite3.connect('database.db')
cursor = database.cursor()

class playCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    global shuffle_Toggle
    shuffle_Toggle = False

    # Plays a song from Youtube or Spotify
    # Spotify is played when the bot detects a spotify link since it beggins with "https://open.spotify.com/track/"
    @nextcord.slash_command(description="Play a song")
    async def play(self, interaction : nextcord.Interaction, search : str):
        
 
        destination = interaction.user.voice.channel
   
        if not interaction.guild.voice_client:
            vc: wavelink.Player = await destination.connect(cls = wavelink.Player)
            
        else:
            if (interaction.guild.voice_client.channel.id != destination.id):
                Player = interaction.guild.voice_client  

                await interaction.guild.voice_client.move_to(destination)
                                
            vc: wavelink.Player = interaction.guild.voice_client
        if (random.randint(0, 1000) == 0) and (not vc.is_playing()): #Rickroll chance if the bot is not playing anything (so it doesnt queue and ruins the surprise effect)
            query: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            query: wavelink.GenericTrack = query[0]
            await vc.play(query)
        
        #query ist eine List und an 
        if re.match(r'^https:\/\/soundcloud\.com', search):
            if re.search(r'\/sets\/', search):
                
                await interaction.response.send_message("Soundcloud Playlists/sets/Albums dont work")
                return
                track_links = get_track_links(search) #i tried using a webscraper, but that didnt work, maybe with soundcloud api it could work
                for link in track_links: 
                    print(link)
                    found: list[wavelink.SoundCloudTrack] = await wavelink.SoundCloudTrack.search(link)
                
                    query: wavelink.GenericTrack = found
                    
                    await vc.queue.put_wait(query)
                    
                if not vc.is_playing():
                    if query != None:
                        await interaction.response.send_message("Error trying to read the Sets/Albums")
                        
                    else:
                        await vc.play(query)
                
                await interaction.response.send_message("Soundcloud Playlist Added To Queue")
                return
            else:
                query : list[wavelink.SoundCloudTrack]= await wavelink.SoundCloudTrack.search(search)
                query : wavelink.GenericTrack = query[0]
                
                embed = playEmbed(query, vc)
                await interaction.response.send_message(embed=embed)
                
                
        elif re.match(r'^https:\/\/www\.youtube\.com\/watch', search):
            if has_list_parameter(search) == True: #allowes private playlist songs to be played, by removing the playlist part in the link
                search = remove_list_parameter(search)
                
                
                query: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
                query: wavelink.GenericTrack = query[0]
                
                embed = playEmbed(query, vc)
                await interaction.response.send_message(embed=embed)
               
                
            else:
                query: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
                query: wavelink.GenericTrack = query[0]
                
                embed = playEmbed(query, vc)
                await interaction.response.send_message(embed=embed)
                
        elif re.match(r'^https:\/\/youtu\.be', search): 
            query: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
            query: wavelink.GenericTrack = query[0]
            
            embed = playEmbed(query, vc)
            await interaction.response.send_message(embed=embed)
            
        elif re.match(r'^https:\/\/open\.spotify\.com', search):
            await interaction.response.send_message(f"Spotify-links funktionieren gerade nicht")
        elif re.match(r'^https:\/\/www\.youtube\.com\/playlist\?list', search):
            playlist: list[wavelink.YouTubeTrack] = await wavelink.YouTubePlaylist.search(search)
            tracks = playlist.tracks
            for track in tracks[1:]:
                query: wavelink.GenericTrack = track
                await vc.queue.put_wait(query)
            if not vc.is_playing():
                query: wavelink.GenericTrack = tracks[0]
               # await vc.queue.put_wait(query)
                await vc.play(query)
                #wavelink.Player.autoplay = True
            await interaction.response.send_message("Youtube Playlist Added To Queue")
            return
        if not vc.is_playing():
            
            await vc.play(query)
        else:
            await vc.queue.put_wait(query)

        #await dj.djCheck(self, interaction, play)
    
    # Disconnects the bot from the VC
    @nextcord.slash_command(description="Disconnects the bot from a VC")
    async def disconnect(self, interaction : nextcord.Interaction):

        #async def disconnect():
            vc: wavelink.Player = interaction.guild.voice_client
            await vc.disconnect()
            await interaction.response.send_message("Disconnected the Bot")
            
            await vc.stop()
        #await dj.djCheck(self, interaction, disconnect)

    # Pauses the current playing song
    @nextcord.slash_command(description="Pause a song")#
    async def pause(self, interaction : nextcord.Interaction): #this might not work

       # async def pause():

            vc: wavelink.Player = interaction.guild.voice_client
            try:
                await vc.pause()
                await interaction.response.send_message("Paused the current song")
            except:
                await interaction.response.send_message("Song is already Pasued!")
        
        #await dj.djCheck(self, interaction, pause)

    # Resumes the current song
    @nextcord.slash_command(description="Pause a song")
    async def resume(self, interaction : nextcord.Interaction):

       # async def resume():
            vc: wavelink.Player = interaction.guild.voice_client
            try:      
                await vc.resume()
                await interaction.response.send_message("Resumed the current song")
            except:
                await interaction.response.send_message("Song is already resumed!")

        #await dj.djCheck(self, interaction, resume)

    # Shows what song is currently playing
    @nextcord.slash_command(description="Shows what currently playing")
    async def whatsplaying(self, interaction : nextcord.Interaction):

        vc: wavelink.Player = interaction.guild.voice_client
        embed = embeds.whatsPlaying(vc)

        try:        
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("Nothing is currently playing")

    # Loops the current song
    @nextcord.slash_command(description="Loops a song")
    async def loop(self, interaction : nextcord.Interaction):
        
        #async def loop():

            vc: wavelink.Player = interaction.guild.voice_client
            if vc.queue.loop:
                vc.queue.loop = False
                print(vc.queue.loop)
                await interaction.response.send_message("Looping is turned off")
            else:
                vc.queue.loop = True
                print(vc.queue.loop)
                await interaction.response.send_message("Looping is turned on")

        #await dj.djCheck(self, interaction, loop)
    
    @nextcord.slash_command(description="Loops the queue")
    async def queue_loop(self, interaction : nextcord.Interaction):

        vc : wavelink.Player = interaction.guild.voice_client
        if vc.queue.loop_all:

            vc.queue.loop_all = False
            await interaction.response.send_message("Queue looping is turned off")
        
        else:
                
            vc.queue.loop_all = True
            await interaction.response.send_message("Queue looping is turned on")
    
    @nextcord.slash_command(description="Replays the current song")
    async def replay(self, interaction : nextcord.Interaction):

        async def replay():
            vc: wavelink.Player = interaction.guild.voice_client
            await vc.play(vc.current)
            await interaction.response.send_message("Replaying the current song")

        #await dj.djCheck(self, interaction, replay)
    
    @nextcord.slash_command(description="Shuffles the songs in the queue")
    async def shuffle(self, interaction : nextcord.Interaction):

        vc : wavelink.Player = interaction.guild.voice_client

        query = "SELECT SHUFFLE FROM guilds WHERE guild_id = ?"
        shuffle_status = cursor.execute(query, (interaction.guild.id,)).fetchone()

        async def shuffle():
            if shuffle_status[0] == 0:
                await interaction.response.send_message("Shuffling the queue")
                cursor.execute("UPDATE guilds SET shuffle = ? WHERE guild_id = ?", (True, interaction.guild.id,))
                database.commit()
                
            else:
                await interaction.response.send_message("Unshuffling the queue")
                cursor.execute("UPDATE guilds SET shuffle = ? WHERE guild_id = ?", (False, interaction.guild.id,))
                database.commit()
    
        
        #await dj.djCheck(self, interaction, shuffle)

    @nextcord.slash_command(description="Seeks a song in seconds")
    async def seek(self, interaction : nextcord.Interaction, seconds : int): #works

        vc: wavelink.Player = interaction.guild.voice_client
        await vc.seek(seconds * 1000)
        await interaction.response.send_message(f"Seeked to {seconds} seconds")
    
    @nextcord.slash_command(description="Rewinds a song in seconds")
    async def rewind(self, interaction : nextcord.Interaction, seconds : int):  #works
            
            vc: wavelink.Player = interaction.guild.voice_client
            await vc.seek(vc.position - (seconds * 1000))
            await interaction.response.send_message(f"Rewinded {seconds} seconds")


def remove_list_parameter(url):
        pattern = r'&list=.*'
        clean_url = re.sub(pattern,'', url)
        return clean_url

def has_list_parameter(url):
    pattern = r'&list='  # Regular expression pattern to match "&list" parameter
    match = re.search(pattern, url)
    return match is not None

def playEmbed(query, vc):
    print("Embed Sent")
    embed = nextcord.Embed(title=f"{query.title}", url=query.uri)
    embed.set_author(name="Added to the queue")
    embed.set_thumbnail(url=query.thumbnail)
    embed.add_field(name="Channel", value=vc.channel.name, inline=True)
    embed.add_field(name="Duration", value=round((query.duration / 1000) / 60, 2), inline=True)
    embed.add_field(name="Position in Queue", value=len(vc.queue) + 1, inline=False)

    return embed

def get_track_links(soundcloud_set_url):#this function is not working, i tried to get the links of the songs in a soundcloud set
    response = requests.get(soundcloud_set_url)
    html_content = response.text
    #soup = BeautifulSoup(html_content, 'html.parser')

    track_links = []
    #tracks = soup.find_all('a', class_='trackItem__trackTitle')
    for track in tracks:
        link = track['href']
        track_links.append(link)

def setup(bot : commands.Bot):
    bot.add_cog(playCommands(bot))