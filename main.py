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
    with open("manifest.txt", "r") as file:
        for line in file.readlines():
            dat = line.split(":")
            template = Template(dat[0])
            i = 2
            while i < 2 + 4 * int(dat[1]):
                p1, p2, p3, p4 = (
                    int(dat[i]),
                    int(dat[i + 1]),
                    int(dat[i + 2]),
                    int(dat[i + 3].strip()),
                )
                template.add_point(p1, p2, p3, p4)
                print(template)
                i += 4
            data.append(template)
    return data


def pasteImg(root, top, ul, lr):
    im = root
    im2 = top.convert("RGBA")

    im2 = im2.resize((lr[0] - ul[0], lr[1] - ul[1]))
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

    @commands.command()
    async def bonobo(self, ctx, users: commands.Greedy[discord.User]):
        available_templates = list(
            filter(lambda t: t.faces == len(users), self.templates)
        )

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
        await ctx.send(file=discord.File(filename="pasted_picture.png", fp=buffer))


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("====================")


bot.add_cog(BonoboCog(bot))
bot.run(TOKEN)
