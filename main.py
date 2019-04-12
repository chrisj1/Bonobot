# Work with Python 3.6
import discord
from PIL import Image
import requests
import sys

TOKEN = sys.argv[1]

client = discord.Client()

def paste(back, top, ur, ll):
	im = Image.open(back)
	im2 = Image.open(top)
	im.paste(im2, ur)
	im.show()
	im.save("pasted_picture.jpg")

@client.event
async def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return

	if message.content.startswith('!bonobo'):
		for i in message.mentions:
			print(i.avatar_url)
			url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(i)
			filename = i.display_name
			r = requests.get(url, allow_redirects=True)
			open(filename, 'wb').write(r.content)
			paste('010318_BB_bonobos_main.jpg', filename, (100,100),(200,200))
			await message.channel.send(file=discord.File('pasted_picture.jpg'))


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run(TOKEN)