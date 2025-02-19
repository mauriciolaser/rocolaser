import sys
import os
import eyed3
from eyed3.id3 import Tag
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Definir la ruta correcta a la carpeta "music"
current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = os.path.join(os.path.dirname(current_dir), 'music')

# Especifica la ruta completa a ffmpeg
# Configuración automática de FFMPEG según el SO
if sys.platform.startswith("win"):
    # Ruta para Windows
    FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"
elif sys.platform.startswith("linux"):
    # Ruta estándar para Ubuntu/Linux
    FFMPEG_PATH = "/usr/bin/ffmpeg"
else:
    # Fallback para otros sistemas (MacOS, etc)
    FFMPEG_PATH = "ffmpeg"  # Asume que está en el PATH
    
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('@rocolaser '), intents=intents)

pending_play_requests = {}

# Array global que contendrá todas las canciones con un ID único
all_songs = []

def get_song_info(filename, path):
    """
    Intenta obtener artista y título usando eyed3.
    Si no hay etiquetas, se usa el nombre del archivo (sin extensión).
    """
    try:
        audiofile = eyed3.load(path)
        if audiofile and audiofile.tag:
            artist = audiofile.tag.artist if audiofile.tag.artist else ""
            title = audiofile.tag.title if audiofile.tag.title else ""
        else:
            artist, title = "", ""
    except Exception as e:
        artist, title = "", ""
    song_info = (artist + " " + title).strip()
    if not song_info:
        song_info = os.path.splitext(filename)[0]
    return artist, title, song_info

def load_all_songs():
    """
    Recorre la carpeta de música y devuelve una lista de diccionarios.
    Cada diccionario contiene:
      - id: número único (empezando en 1)
      - filename: nombre del archivo
      - artist, title, song_info: datos obtenidos (o el nombre de archivo como fallback)
      - path: ruta completa al archivo
    """
    songs = []
    if os.path.exists(music_dir):
        for filename in os.listdir(music_dir):
            if filename.endswith('.mp3'):
                path = os.path.join(music_dir, filename)
                artist, title, song_info = get_song_info(filename, path)
                song_id = len(songs) + 1
                songs.append({
                    'id': song_id,
                    'filename': filename,
                    'artist': artist,
                    'title': title,
                    'song_info': song_info,
                    'path': path
                })
    return songs

# Comando prefijo /refresh: actualiza la lista de canciones
@bot.command(name='refresh')
async def refresh(ctx):
    global all_songs
    all_songs = load_all_songs()
    await ctx.send(f"✅ Lista de canciones actualizada. {len(all_songs)} canciones cargadas.")

# Comando slash /refresh: actualiza la lista de canciones
@bot.tree.command(name="refresh", description="Actualiza la lista de canciones desde el directorio /music")
async def slash_refresh(interaction: discord.Interaction):
    global all_songs
    all_songs = load_all_songs()
    await interaction.response.send_message(f"✅ Lista de canciones actualizada. {len(all_songs)} canciones cargadas.")

@bot.event
async def on_ready():
    global all_songs
    all_songs = load_all_songs()
    await bot.tree.sync()  # Sincroniza los comandos slash con Discord
    print(f'{bot.user} ha iniciado sesión en Discord')
    print(f"Se cargaron {len(all_songs)} canciones.")

# Comando prefijo /lista: ahora muestra la lista de canciones con su número
@bot.command(name='lista')
async def lista(ctx):
    if not all_songs:
        await ctx.send("❌ No hay archivos MP3 en /music")
        return

    response = "🎵 **Lista de Canciones:**\n"
    for song in all_songs:
        response += f"{song['id']}. {song['song_info']}\n"
    await ctx.send(response)

# Comando slash /lista: muestra la lista de canciones con su número
@bot.tree.command(name="lista", description="Lista las canciones en /music con su número")
async def slash_lista(interaction: discord.Interaction):
    if not all_songs:
        await interaction.response.send_message("❌ No hay archivos MP3 en /music", ephemeral=True)
        return

    response = "🎵 **Lista de Canciones:**\n"
    for song in all_songs:
        response += f"{song['id']}. {song['song_info']}\n"
    await interaction.response.send_message(response)

@bot.command(name='play')
async def play(ctx, *, search_query):
    if not ctx.author.voice:
        await ctx.send("⚠️ Debes estar en un canal de voz")
        return

    if not os.path.exists(music_dir):
        await ctx.send("❌ La carpeta `/music` no existe")
        return

    matches = []
    for filename in os.listdir(music_dir):
        if filename.endswith('.mp3'):
            path = os.path.join(music_dir, filename)
            artist, title, song_info = get_song_info(filename, path)
            if search_query.lower() in song_info.lower():
                matches.append((artist, title, path))

    if not matches:
        await ctx.send("🔍 No se encontraron canciones")
        return

    matches = matches[:10]  # Limitar a 10 resultados

    options = "\n".join(
        [f"{idx+1}. {artist} - {title}" if artist and title else f"{idx+1}. {os.path.basename(path)}"
         for idx, (artist, title, path) in enumerate(matches)]
    )

    await ctx.send(
        f"🔍 **Resultados para '{search_query}':**\n{options}\n"
        "**Escribe el número de la canción para reproducir**"
    )

    pending_play_requests[ctx.author.id] = [path for (_, _, path) in matches]

@bot.tree.command(name="play", description="Busca y reproduce una canción en el canal de voz")
async def slash_play(interaction: discord.Interaction, search_query: str):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ Debes estar en un canal de voz", ephemeral=True)
        return

    if not os.path.exists(music_dir):
        await interaction.response.send_message("❌ La carpeta `/music` no existe", ephemeral=True)
        return

    matches = []
    for filename in os.listdir(music_dir):
        if filename.endswith('.mp3'):
            path = os.path.join(music_dir, filename)
            artist, title, song_info = get_song_info(filename, path)
            if search_query.lower() in song_info.lower():
                matches.append((artist, title, path))

    if not matches:
        await interaction.response.send_message("🔍 No se encontraron canciones", ephemeral=True)
        return

    matches = matches[:10]  # Limitar a 10 resultados

    options = "\n".join(
        [f"{idx+1}. {artist} - {title}" if artist and title else f"{idx+1}. {os.path.basename(path)}"
         for idx, (artist, title, path) in enumerate(matches)]
    )

    await interaction.response.send_message(
        f"🔍 **Resultados para '{search_query}':**\n{options}\n"
        "**Escribe el número de la canción para reproducir**"
    )

    pending_play_requests[interaction.user.id] = [path for (_, _, path) in matches]

@bot.command(name='join')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("⚠️ Debes estar en un canal de voz para que me conecte.")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client

    if voice_client and voice_client.is_connected():
        await voice_client.move_to(voice_channel)
    else:
        await voice_channel.connect()

    await ctx.send(f"✅ Me he unido a {voice_channel.name}")

@bot.tree.command(name="join", description="Hace que el bot se una a tu canal de voz")
async def slash_join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ Debes estar en un canal de voz para que me conecte.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.move_to(voice_channel)
    else:
        await voice_channel.connect()
    await interaction.response.send_message(f"✅ Me he unido a {voice_channel.name}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user or not message.content.isdigit():
        return

    user_id = message.author.id
    if user_id not in pending_play_requests:
        return

    try:
        num = int(message.content)
        songs = pending_play_requests[user_id]

        if num < 1 or num > len(songs):
            await message.channel.send("❌ Número inválido")
            del pending_play_requests[user_id]
            return

        path = songs[num-1]
        del pending_play_requests[user_id]

        voice_channel = message.author.voice.channel
        voice_client = message.guild.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.stop()

        if not voice_client:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        voice_client.play(discord.FFmpegPCMAudio(path, executable=FFMPEG_PATH))
        await message.channel.send(f"🎶 Reproduciendo: `{os.path.basename(path)}`")

    except Exception as e:
        await message.channel.send(f"❌ Error: {str(e)}")

# --- Comandos nuevos para reproducir por número usando la lista global ---

# Comando prefijo /code: reproduce la canción por su número (según all_songs)
@bot.command(name='code')
async def code(ctx, number: int):
    if not ctx.author.voice:
        await ctx.send("⚠️ Debes estar en un canal de voz")
        return
    if number < 1 or number > len(all_songs):
        await ctx.send("❌ Número inválido")
        return
    song = all_songs[number - 1]
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    if not voice_client:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)
    voice_client.play(discord.FFmpegPCMAudio(song['path'], executable=FFMPEG_PATH))
    await ctx.send(f"🎶 Reproduciendo: {song['song_info']}")

# Comando slash /code: reproduce la canción por su número (según all_songs)
@bot.tree.command(name="code", description="Reproduce la canción por su número")
async def slash_code(interaction: discord.Interaction, number: int):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ Debes estar en un canal de voz", ephemeral=True)
        return
    if number < 1 or number > len(all_songs):
        await interaction.response.send_message("❌ Número inválido", ephemeral=True)
        return
    song = all_songs[number - 1]
    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    if not voice_client:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)
    voice_client.play(discord.FFmpegPCMAudio(song['path'], executable=FFMPEG_PATH))
    await interaction.response.send_message(f"🎶 Reproduciendo: {song['song_info']}")

bot.run(TOKEN)
