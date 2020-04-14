# Work with Python 3.6
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps
import requests
import sys
import random

TOKEN = sys.argv[1]

bot = commands.Bot(command_prefix='!')

class Template:
	filename = ""
	points = []
	def __init__(self, filename):
		self.filename = filename
		self.points = []

	def add_point(self, ulx, uly, lrx, lry):
		self.points.append((ulx, uly, lrx, lry))

	def upperleftcord(self, i):
		return (self.points[i][0], self.points[i][1])

	def lowerrightcord(self, i):
		return (self.points[i][2], self.points[i][3])

	@property
	def faces(self):
		return len(self.points)

	def __str__(self):
		return f"filename: {self.filename}, points={self.points}"

	def __repr__(self):
		return self.__str__()


def parseManifest():
	data = []
	with open('manifest.txt', 'r') as file:
		for line in file.readlines():
			dat = line.split(":")
			print(dat)
			print(int(dat[1]))
			template = Template(dat[0])
			i = 2
			while i < 2 + 4 * int(dat[1]):
				p1, p2, p3, p4 = int(dat[i]), int(dat[i + 1]), int(dat[i + 2]), int(dat[i + 3].strip())
				template.add_point(p1, p2, p3, p4)
				print(template)
				i += 4
			data.append(template)
	return data


def pasteImg(back, top, ul, lr, root):
	im = root
	if im is None:
		im = back.convert('RGBA')
	im2 = top.convert('RGBA')

	im2 = im2.resize((lr[0] - ul[0], lr[1] - ul[1]))
	im.paste(im2, ul, im2)
	return im


class BonoboCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.templates = parseManifest()

	@commands.command()
	async def bonobo(self, ctx, users: commands.Greedy[discord.User], *):
		im = None

		template = random.choice(filter(lambda t: t.faces == len(users), self.templates))                                                                                                                                                         

		if template is not None:
			back = Image.open(template.filename)

			for count, user in enumerate(users):
				url = user.avatar_url_as(static_format='png', size=1024)
				top = Image.open(requests.get(url, allow_redirects=True, stream=True).raw)
				im = pasteImg(back, top, template.upperleftcord(count), template.lowerrightcord(count), im)
	
			buffer = BytesIO()
			im.save(buffer, 'png')
			file = discord.File(filename='pasted_picture.png', fp=buffer)
			await ctx.send(file=file)


@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('====================')


bot.add_cog(BonoboCog(bot))
bot.run(TOKEN)
