# Work with Python 3.6
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps
import aiohttp
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


def pasteImg(root, top, ul, lr):
	im = root
	im2 = top.convert('RGBA')

	im2 = im2.resize((lr[0] - ul[0], lr[1] - ul[1]))
	im.paste(im2, ul, im2)
	return im


class BonoboCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.templates = parseManifest()
		self.session = aiohttp.ClientSession(loop=bot.loop)

	async def get_avatar(self, user: Union[discord.User, discord.Member]) -> BytesIO:
		avatar_url = user.avatar_url_as(format='png', size=1024)
		avatar_bytes = None
		async with self.session.get(avatar_url) as response:
			avatar_bytes = await response.read()
		return BytesIO(avatar_bytes)
		
	@commands.command()
	async def bonobo(self, ctx, users: commands.Greedy[discord.User], *):
		template = random.choice(filter(lambda t: t.faces == len(users), self.templates))                                                                                                                                                         

		if template is not None:
			im = Image.open(template.filename).convert('RGBA')

			for count, user in enumerate(users):
				top_buff = await self.get_avatar(user)
				with Image.open(top_buff) as top:
					im = pasteImg(im, top, template.upperleftcord(count), template.lowerrightcord(count))
	
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
