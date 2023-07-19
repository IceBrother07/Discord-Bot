import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
import asyncio
import requests
from bs4 import BeautifulSoup
import re
import random
import os,json
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time




intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

@bot.command()
async def leave(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("I'm not connected to a voice channel.")

@bot.command()
async def play(ctx, url):
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if not voice_client or not voice_client.is_connected():
        await ctx.send("I'm not connected to a voice channel. Use $join to summon me.")
        return

    if not ctx.author.voice or voice_client.channel != ctx.author.voice.channel:
        await ctx.send("You are not connected to the same voice channel as me.")
        return

    voice_channel = ctx.author.voice.channel
    try:
        await voice_channel.connect()
    except discord.ClientException:
        pass

    voice_client = get(bot.voice_clients, guild=ctx.guild)
    voice_client.stop()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  
        'force-ipv4': True,
        'preferredcodec': 'mp3',
        'cachedir': False
    }
    ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        
    voice_client.play(FFmpegPCMAudio(url2,**ffmpeg_options))
    while voice_client.is_playing():
     await asyncio.sleep(1)

@bot.command()
async def pula(ctx):
    username_list=['.husbandowo',".melones"]
    if str(ctx.author) not in username_list:
        await ctx.send(f'{ctx.author} are pula mica')
    else: await ctx.send(f'{ctx.author} are pula mare')

@bot.command()
async def anime(ctx):
    url = 'https://myanimelist.net/anime/season'
    
    response = requests.get(url)
    html_content = response.text
    web_page = BeautifulSoup(html_content, 'html.parser')
    anime_url=web_page.find_all('div',{'class':re.compile('js-anime-category-producer seasonal-anime js-seasonal-anime')})
    anime_list=[]
    for anime in anime_url:
        anime_list.append(anime.find('div',class_='image').a['href'])
    if random.randint(0,100)==10:
        await ctx.send('Best Anime:\n https://myanimelist.net/anime/40935/Beastars_2nd_Season?q=beastars&cat=anime')
    else:
        await ctx.send(anime_list[random.randint(0,len(anime_list)-1)])

@bot.command()
async def rank(ctx):
    rank_list=['bronze 4','bronze 3','bronze 2','bronze 1','silver 4','silver 3','silver 2','silver 1','gold 4','gold 3','gold 2','gold 1','platinum 4','platinum 3','platinum 2','platinum 1','diamond 4','diamond 3','diamond 2','diamond 1']
    lol_url = 'https://www.op.gg/summoners/eune/Angura%20Samiliei'
    response = HTMLSession().get(lol_url)
    html_content = response.text
    web_page = BeautifulSoup(html_content, 'html.parser')
    try:
        rank=web_page.find('div',{"class":'tier'}).text

        lp=web_page.find('div',{"class":'lp'}).text
    except:
        await ctx.send("Didn't play ranked this season :(\nYET :)")
        return 0


    info={"rank":rank,"lp":lp}
    file="lol_status.json"
    if not os.path.isfile(file):
        with open(file,"w") as f:
            json.dump(info,f)
            f.close()
    with open(file,'r') as f:
        old_info=json.load(f)
        f.close()
    if old_info!=info:
        rank_status=rank_list.index(old_info['rank'])-rank_list.index(info['rank'])
        if rank_status==0:
            lp_status=int(''.join((lp) for lp in old_info["lp"].split() if lp.isdigit()))-int(''.join((lp) for lp in info["lp"].split() if lp.isdigit()))
            if lp_status>0:
                await ctx.send(f"Dumbass lost {lp_status} lp since last checkup")
            else: await ctx.send(f"Fatass gained {lp_status*-1} lp since last checkup")
        else: await ctx.send(f"Fatso went from:\n{old_info['rank']} {old_info['lp']}\nto:\n{info['rank']} {info['lp']}")
    else: await ctx.send(f"Good job your rank hasn't changed:\n{old_info['rank']} {old_info['lp']}\nYou have a life")
    with open(file,'w') as f:
        json.dump(info,f)
        f.close()



@bot.command()
async def myanime(ctx,url):
    if url==None:
        await ctx.send('Please input an URL')
        return
    options = webdriver.ChromeOptions()

    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    for i in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    web_page = BeautifulSoup(driver.page_source, 'html.parser')
    anime_url=web_page.find_all('td',{'class':'data title clearfix'})
    anime_list=[]
    for anime in anime_url:
        anime_list.append('https://myanimelist.net'+str(anime.a['href']))
    if random.randint(0,100)==10:
        await ctx.send('Best Anime:\n https://myanimelist.net/anime/40935/Beastars_2nd_Season?q=beastars&cat=anime')
    else:
        await ctx.send(anime_list[random.randint(0,len(anime_list)-1)])


bot.run('MTEyMjk5NDI0MTA5NDgzMjE5OQ.GnyzLJ.iX2EhYLyYJ6Z55p4MlasUOcNXfZQaZSImOxSB8')