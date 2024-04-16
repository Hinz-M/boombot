import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelink
import re
import cogs.embeds as embeds



class comsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @nextcord.slash_command( name="remoteplay", description="plays music for someone")#guild_ids=[501121938840616971]
    async def remoteplay(self, interaction : nextcord.Interaction, member: nextcord.Member, *, query: str):
        print(member)
        print(query)

        
        
        if not interaction.guild.voice_client:
            if member.voice and member.voice.channel:
                
                vc: wavelink.Player = await member.voice.channel.connect(cls = wavelink.Player)

            else:
                await interaction.response.send_message(f"{member.mention} is not in a voice channel.")
 
        search = query    
        if re.match(r'^https:\/\/soundcloud\.com', query):
            if re.search(r'\/sets\/', query):
                
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
                #await interaction.response.send_message(embed=embed)
                
        elif re.match(r'^https:\/\/youtu\.be', search): 
            query: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
            query: wavelink.GenericTrack = query[0]
            
            #embed = playEmbed(query, vc)
            #await interaction.response.send_message(embed=embed)
            
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
        await interaction.response.send_message(f"Playing {query} for {member.mention}")
    @nextcord.slash_command( name="rickroll", description="rickrolls someone")#guild_ids=[501121938840616971]
    async def rickroll(self, interaction : nextcord.Interaction, member: nextcord.Member):
        print(member)
        if not interaction.guild.voice_client:
            if member.voice and member.voice.channel:
                
                vc: wavelink.Player = await member.voice.channel.connect(cls = wavelink.Player)

            else:
                await interaction.response.send_message(f"{member.mention} is not in a voice channel.")
                
        query: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        query: wavelink.GenericTrack = query[0]
        await vc.play(query)   
        await interaction.response.send_message(f"{member.mention} got rickrolled")
        

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


def setup(bot : commands.Bot):
    bot.add_cog(comsCommands(bot))
    
