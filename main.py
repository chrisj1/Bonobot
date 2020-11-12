# Work with Python 3.6
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO
import aiohttp
import sys
import random
from typing import Union
from io import BytesIO
import imageio
import os

try:
    TOKEN = sys.argv[1]
except:
    print("ERROR: argv[1] is missing - no discord token supplied!", file=sys.stderr)
    sys.exit(1)

bot = commands.Bot(command_prefix="!")


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
    for filename in os.listdir('autotemplates'):
        if filename[-9:] == "_mask.png":
            template = Template(f'autotemplates/{filename[:-9]}.png')
            im = imageio.imread(f'autotemplates/{filename}')
            startingpoints = []
            for y in range(im.shape[0]):
                for x in range(im.shape[1]):
                    if im[y][x][0] == 0:
                        if(im[y-1][x][0] != 0 and im[y][x-1][0] != 0):
                            startingpoints.append((x,y))

            for x_1, y_1 in startingpoints:
                x_2, y_2 = x_1,y_1
                while (im[y_2][x_2][0] != 255):
                    y_2 += 1
                y_2-=1
                while (im[y_2][x_2][0] != 255):
                    x_2 += 1
                template.add_point(x_1, y_1, x_2, y_2)
            data.append(template)
            print(startingpoints)
    return data


def pasteImg(root, top, ul, lr):
    im = root
    im2 = top.convert("RGBA")
    im2 = im2.resize((abs(lr[0] - ul[0]), abs(lr[1] - ul[1])))
    im.paste(im2, ul, im2)
    return im


class BonoboCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.templates = parseManifest()
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> Image:
        avatar_url = user.avatar_url_as(format="png", size=1024)
        response = await self.session.get(str(avatar_url))
        avatar_bytes = await response.read()
        return Image.open(BytesIO(avatar_bytes))

    @commands.command(aliases=["bonobot"])
    async def bonobo(self, ctx, users: commands.Greedy[discord.User]):
        available_templates = list(
            filter(lambda t: t.faces == len(users), self.templates)
        )

        # Randomize the images for maximum fun
        random.shuffle(users)

        if len(available_templates) == 0:
            await ctx.send("Invalid usage.")
            return

        template = random.choice(available_templates)
        im = Image.open(template.filename).convert("RGBA")
        for count, user in enumerate(users):
            top = await self.get_avatar(user)
            im = pasteImg(
                im, top, template.upperleftcord(count), template.lowerrightcord(count)
            )

        buffer = BytesIO()
        im.save(buffer, "png")
        buffer.seek(0)
        await ctx.send(file=discord.File(filename="love.png", fp=buffer))


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("====================")


bot.add_cog(BonoboCog(bot))
bot.run(TOKEN)
