# Work with Python 3.6
import discord
from PIL import Image,ImageDraw,ImageOps
import requests
import sys
from random import shuffle

TOKEN = sys.argv[1]

client = discord.Client()

templates = []

class Template:
	filename = ""
	points = []
	def __init__(self, filename):
		self.filename = filename
		self.points=[]

	def add_point(self, ulx, uly,lrx,lry):
		self.points.append((ulx, uly, lrx,lry))

	def upperleftcord(self,i):
		return (self.points[i][0],self.points[i][1])

	def lowerrightcord(self,i):
		return (self.points[i][2],self.points[i][3])

	def faces(self):
		return len(self.points)

	def __str__(self):
		return "filename: {}, points={}".format(self.filename, self.points)

	def __repr__(self):
		return self.__str__()


def parseManifest():
	with open('manifest.txt', 'r') as file:
		lines = file.readlines()
		data = []
		print(lines)
		for line in lines:
			dat = line.split(":")
			print(dat)
			print(int(dat[1]))
			template = Template(dat[0])
			i = 2
			while i < 2 + 4 * int(dat[1]):
				template.add_point(int(dat[i]), int(dat[i + 1]), int(dat[i + 2]), int(dat[i + 3].strip()))
				print(template)
				i+=4
			data.append(template)
		print(data)
		return data



def paste(back, top, ul, lr, root):
	im = root
	if im is None:
		im = Image.open(back).convert('RGBA')
	im2 = Image.open(top).convert('RGBA')

	print(lr[0] - ul[0], lr[1] - ul[1])
	im2 = im2.resize((lr[0] - ul[0], lr[1] - ul[1]))
	im.paste(im2, ul, im2)
	im.save("pasted_picture.png")
	return im


@client.event
async def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return

	if message.content.startswith('!bonobo') and len(message.mentions) > 0:
		im = None
		global templates
		shuffle(templates)
		for template in templates:
			count = 0
			if template.faces() is len(message.mentions):
				for i in message.mentions:
					print(i.display_name)
					url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(i)
					filename = i.display_name
					r = requests.get(url, allow_redirects=True)
					open(filename, 'wb').write(r.content)
					im = paste(template.filename, filename, template.upperleftcord(count),template.lowerrightcord(count), im)
					count+=1
				await message.channel.send(file=discord.File('pasted_picture.png'))
				break


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('====================')
	global templates
	templates = parseManifest()

client.run(TOKEN)
