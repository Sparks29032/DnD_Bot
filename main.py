import discord

import os
from dotenv import load_dotenv

import re
import random

load_dotenv()
__TOKEN__ = os.getenv('TOKEN')
__ID__ = int(os.getenv('ID'))
resources_dir = os.path.join(os.getcwd(), "Resources")
ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} is online.')

@client.event
async def on_message(message):
    # avoid recursion
    if message.author == client.user:
        return

    # message information
    author = message.author
    channel = message.channel
    guild = message.guild
    original_content = message.content
    content = message.content.lower()

    # check if role mentioned
    role_mentioned = False
    bot = guild.get_member(__ID__)
    for role in bot.roles:
        if role in message.role_mentions:
            role_mentioned = True

    # if bot or role mentioned
    if client.user.mentioned_in(message) or role_mentioned:
        print(f'({author}) {content}')

        def leave_voice():
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    return vc.disconnect(force=False)

        # leave voice channel if requested
        if bot.voice is not None:
            vc_curr = None
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    vc_curr = vc

            if re.search(r".*leave.*(voice|call).*", content):
                await leave_voice()
                return

            # play existing audio file
            if re.search(r".*play.*", content):
                playing = False

                # find local file to play
                for mf in os.listdir(resources_dir):
                    if mf in original_content:
                        audio_source = os.path.join(resources_dir, mf)
                        vc_curr.play(discord.FFmpegPCMAudio(executable=ffmpeg, source=audio_source))
                        playing = True
                        print(f"Playing... {mf}")
                        await channel.send(f"Playing from file {mf}...")
                        break

                # # find youtube file to play
                # if not playing:
                #     mts = original_content.split(" ")
                #     song_urls = set()
                #     for mt in mts:
                #         if "http://" in mt or "https://" in mt:
                #             song_urls.add(mt.strip())
                #     if len(song_urls) == 1:
                #         player = await vc_curr.create_ytdl_player(list(song_urls)[0])
                #         player.start()
                #         playing = True
                #     elif len(song_urls) > 1:
                #         await channel.send(f"What am I supposed to do with all these links? Give me one!")
                #         playing = True

                if not playing:
                    await channel.send(f"Never heard of that song. (I am case sensitive.)")
                return

        # join voice channel if requested
        if re.search(r".*join.*(voice|call).*", content):
            if author.voice is not None:
                if bot.voice is not None:
                    await leave_voice()
                await author.voice.channel.connect()
            else:
                voice_channels = []

                for ch in message.channel_mentions:
                    if 'voice' in ch.type:
                        voice_channels.append(ch)

                if len(voice_channels) == 1:
                    if bot.voice is not None:
                        await leave_voice()
                    await voice_channels[0].connect()
                else:
                    await channel.send('What channel am I supposed to join?')
            return

        if re.search(r".*roll.*d[0-9]+.*", content):
            re_match = re.search(r"d[0-9]+", content)
            try:
                dice_size = int(re_match.group(0)[1:])
                if dice_size < 1:
                    await channel.send(f'The dice in my home have positive numbers of faces.')
                else:
                    await channel.send(f'Rolling... {random.randint(1, dice_size)}!')
            except ValueError:
                await channel.send(f'What kinds of dice do you play with? I cannot roll a {re_match}.')
            return

        # unknown action
        await channel.send('What do you want?')
        return

client.run(__TOKEN__)
