import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelink
#from wavelink.ext import spotify
import sqlite3


import random

basedata = sqlite3.connect('basedata.db')
cursor = basedata.cursor()

class radioCommands(commands.Cog):
       def __init__(self, bot):
              self.bot = bot
       async def play_radio(self, vc: wavelink.Player): #interaction : nextcord.Interaction
              #vc: wavelink.Player = interaction.guild.voice_client #no cord
              #vc: wavelink.Player = interaction.player#no cord
              if not vc.is_connected:#prevents the programm/bot to search for songs when not connected to a vc
                     print("exiting")
                     return
              guild_id = vc.guild.id
              cursor.execute("SELECT radio FROM guilds WHERE guild_id = ?", (guild_id,))
              radio_activated = cursor.fetchone()[0]
              if radio_activated:
                     # Select a random playlist from the radio table
                     cursor.execute("SELECT Playlist FROM radio WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1", (guild_id,))
                     playlist_link = cursor.fetchone()[0]
                     # Fetch the playlist
                     #tracks = await wavelink.YouTubePlaylist.search(playlist_link)  #no cord
                     playlist = await wavelink.YouTubePlaylist.search(playlist_link)
                     #tracks = [await wavelink.YouTubeTrack.search(track.uri) for track in playlist.tracks]
                     tracks = [track for sublist in [await wavelink.YouTubeTrack.search(track.uri) for track in playlist.tracks] for track in sublist]
                     # Select a random track
                     
                     track = random.choice(tracks)

                     # Play the track
                     await vc.play(track)     
       @nextcord.slash_command(name="radio", description="Radio Commands") #, guild_ids=[1008448013678674051]
       async def radio(self, interaction : nextcord.Interaction): #: nextcord.Interaction

              pass
       @radio.subcommand(description="Turn the Radio on or off")
       async def toggle(self, interaction : nextcord.Interaction):
              # Fetch the current radio status
              cursor.execute("SELECT radio FROM guilds WHERE guild_id = ?", (interaction.guild.id,))
              radio_activated = cursor.fetchone()[0]

              # Toggle the radio status
              new_status = not radio_activated
              cursor.execute("UPDATE guilds SET radio = ? WHERE guild_id = ?", (new_status, interaction.guild.id))
              basedata.commit()

              # Send a confirmation message to the user
              status_str = "on" if new_status else "off"
              await interaction.response.send_message(f"Radio turned {status_str}.")
       
              
       @radio.subcommand(description="Shows the Playlists that are in the Radio")
       async def showlists(self, interaction : nextcord.Interaction):
       # Select all playlists from the radio table
              cursor.execute("SELECT Playlist FROM radio WHERE guild_id = ?", (interaction.guild.id,))
              playlists = cursor.fetchall()

              # Format the playlists into a string
              playlists_str = "\n".join([playlist[0] for playlist in playlists])

              # Send the playlists to the user
              await interaction.response.send_message(playlists_str)

              
       @radio.subcommand(description="Add a Playlist to the Radio")
       async def add(self, interaction : nextcord.Interaction, search : str):
              # Insert the playlist link into the radio table
              cursor.execute("INSERT INTO radio (guild_id, Playlist) VALUES (?, ?)", (interaction.guild.id, search))
              basedata.commit()

              # Send a confirmation message to the user
              await interaction.response.send_message(f"Playlist {search} added to the radio.")

       @radio.subcommand(description="Remove a Playlist from the Radio")
       async def remove(self, interaction : nextcord.Interaction, index: int):
              # Select all playlists from the radio table
              cursor.execute("SELECT Playlist FROM radio WHERE guild_id = ?", (interaction.guild.id,))
              playlists = cursor.fetchall()

              # Check if the index is valid
              if 1 <= index <= len(playlists):
                     # Remove the selected playlist from the radio table
                     playlist_to_remove = playlists[index - 1][0]
                     cursor.execute("DELETE FROM radio WHERE guild_id = ? AND Playlist = ?", (interaction.guild.id, playlist_to_remove))
                     basedata.commit()

                     # Send a confirmation message to the user
                     await interaction.response.send_message(f"Playlist {playlist_to_remove} removed from the radio.")
              else:
                     # Send an error message to the user
                     await interaction.response.send_message("Invalid index.")
                     
def setup(bot : commands.Bot):
    bot.add_cog(radioCommands(bot))
