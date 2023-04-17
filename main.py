import asyncio
import yaml
import discord
import bot_builder as bot_builder
import ytdl_options as ydl_opts
import yt_dlp as youtube_dl

bot = bot_builder.build_bot()
song_queue = []
song_index = 0

def play_next(context):

    global song_index

    def after_playing(error):

        global song_index

        if error:
            print(f"Error while playing audio: {error}")
        else:
            # Play the next song in the queue
            song_index += 1
            bot.loop.create_task(play_next(context))

    # Send a message after the audio finishes playin
    asyncio.run_coroutine_threadsafe(context.send("Now playing: "+ song_queue[song_index]["name"]), bot.loop)
    context.voice_client.play(discord.FFmpegPCMAudio(song_queue[song_index]['url'], 
                                                         executable='D:/FFMPeg/bin/ffmpeg.exe', 
                                                         options= '-vn', 
                                                         before_options= "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",),
                                                         after=after_playing)
    print("SONG INDEX: " + str(song_index))

    return asyncio.sleep(0.1)



@bot.command(aliases=['p', 'P'])
async def play(context, *, song_name):
    global song_index
    voice_state = context.author.voice

    if voice_state:
        if context.voice_client is None:
            await voice_state.channel.connect()

    else: 
        await context.send("You need to be connected to a voice channel.")
        return

    song_info = get_song_info(song_name)
    song_url = song_info["url"]
    song_queue.append({'url': song_url, 'name': song_info["fulltitle"]})

    
    if context.voice_client.is_playing():
        await context.send("Added to queue " + song_info["fulltitle"])
        return
    
    elif song_queue[song_index] is not None:
        play_next(context)


@bot.command()
async def pause(context):
    
    if context.voice_client.is_playing():
        context.voice_client.pause()
        await context.send("Paused the player")
    
    elif context.voice_client.is_paused():
        context.voice_client.resume()
        await context.send("Resumed playing")
    
    else:
        await context.send("I'm currently not playing anything")


@bot.command(aliases=['n','s','skip'])
async def next(context):
    global song_index

    if song_index == len(song_queue) -1:
        await context.send("There are no songs to play next in the queue")
    
    elif context.voice_client is not None:
        if context.voice_client.is_playing():
            context.voice_client.stop()
    

@bot.command(aliases=['prev'])
async def previously(context):
    global song_index

    if song_index <= 0:
        await context.send("There's no song previously on the queue")

    else: 
        song_index -= 2
        if context.voice_client.is_playing():
            context.voice_client.stop()
        else: 
            play_next()

@bot.command(aliases=["q"])
async def queue(context):
    formatted_queue = "**CURRENT QUEUE** \n\n>>> "
    
    for i, item in enumerate(song_queue, 1):
        formatted_queue += "  **" +str(i) + "**"  + ". " + item["name"] + "\n"

    await context.send(formatted_queue)
    
@bot.command(aliases=['i'])
async def index(context):
    global song_index
    print('INDEX: ' + str(song_index))
def get_song_info(query):
    with youtube_dl.YoutubeDL(ydl_opts.data) as ydl:

        try:
            info = ydl.extract_info(f"ytsearch: {query}", download=False)['entries'][0]
            return info

        except Exception as e:
            print(e)


config = yaml.safe_load(open("config.yaml", "r"))
bot_token = config["bot"]["token"]
bot.run(bot_token)