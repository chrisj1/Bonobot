# Work with Python 3.6'
from __future__ import unicode_literals
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
import os.path

try:
    TOKEN = os.environ["BONOBOT_TOKEN"]
except:
    print(
        "ERROR: environment variable BONOBOT_TOKEN is missing - no discord token supplied!",
        file=sys.stderr,
    )
    sys.exit(1)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


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

    def __eq__(self, other):
        return other.filename == self.filename

    def __hash__(self):
        return hash(self.filename)


def parseManifest():
    data = set()
    if not os.path.exists("manifestcache.txt"):
        f = open("manifestcache.txt", "w")
        f.close()
    with open("manifestcache.txt", "r") as f:
        for line in f.readlines():
            d = line.strip().split(" ")
            filename = d[0]
            template = Template(filename)
            print(d)
            for i in range(1, len(d), 4):
                x_1, y_1, x_2, y_2 = (
                    int(d[i]),
                    int(d[i + 1]),
                    int(d[i + 2]),
                    int(d[i + 3]),
                )
                template.add_point(x_1, y_1, x_2, y_2)
            data.add(template)
            print(f"Loaded template for {filename}")
    with open("manifestcache.txt", "a") as f:
        for filename in os.listdir("autotemplates"):
            template = Template(f"autotemplates/{filename[:-9]}.png")
            if filename[-9:] == "_mask.png":
                if template in data:
                    continue
                template = Template(f"autotemplates/{filename[:-9]}.png")
                im = imageio.imread(f"autotemplates/{filename}")
                startingpoints = []
                for y in range(im.shape[0]):
                    for x in range(im.shape[1]):
                        if im[y][x][0] == 0:
                            if im[y - 1][x][0] != 0 and im[y][x - 1][0] != 0:
                                startingpoints.append((x, y))

                height, width, _ = im.shape
                for x_1, y_1 in startingpoints:
                    x_2, y_2 = x_1, y_1
                    while y_2 < height and im[y_2][x_2][0] != 255:
                        y_2 += 1
                    y_2 -= 1
                    while x_2 < width and im[y_2][x_2][0] != 255:
                        x_2 += 1
                    template.add_point(x_1, y_1, x_2, y_2)
                data.add(template)
                s = ""
                for point in template.points:
                    s += str(point[0]) + " "
                    s += str(point[1]) + " "
                    s += str(point[2]) + " "
                    s += str(point[3]) + " "
                f.write(f"autotemplates/{filename[:-9]}.png " + s[:-1] + "\n")
                print(f"Saved template as autotemplates/{filename[:-9]}.png " + s[:-1])
    return data


def pasteImg(root, top, ul, lr):
    im = root
    im2 = top.convert("RGBA")
    im2 = im2.resize((abs(lr[0] - ul[0]), abs(lr[1] - ul[1])))
    im.paste(im2, ul, im2)
    return im


class LazyRandom:
    def __init__(self):
        pass


class DiscordMonke(discord.ext.commands.converter.Converter):
    async def convert(self, ctx, argument: str):
        if argument.lower() in ["random", "rng"]:
            return LazyRandom()

        try:
            return await commands.converter.MemberConverter().convert(ctx, argument)
        except:
            return await commands.converter.EmojiConverter().convert(ctx, argument)


def get_best_random(users, members):
    currRandom = set()
    for i in range(len(users)):
        if isinstance(users[i], LazyRandom):
            if len(currRandom) >= len(members):
                # just do regular sampling
                users[i] = random.choice(members)
                continue

            # find unique random member
            candidate = random.choice(members)
            while candidate in currRandom:
                candidate = random.choice(members)

            currRandom.add(candidate)
            users[i] = candidate


class BonoboCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.templates = parseManifest()
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def get_avatar(
        self, user: Union[discord.User, discord.Member, discord.emoji.Emoji]
    ) -> Image:
        if isinstance(user, discord.emoji.Emoji):
            avatar_url = user.url_as(format="png")
        else:
            avatar_url = user.avatar_url_as(format="png", size=1024)
        response = await self.session.get(str(avatar_url))
        avatar_bytes = await response.read()
        return Image.open(BytesIO(avatar_bytes))

    @commands.command(aliases=["bonobot"])
    async def bonobo(self, ctx, users: commands.Greedy[DiscordMonke]):
        if len(users) == 0 and len(ctx.message.clean_content.split()) == 1:
            users = [LazyRandom()] * random.choice(tuple(self.templates)).faces
            get_best_random(
                users,
                ctx.guild.members,
            )

        available_templates = list(
            filter(lambda t: t.faces == len(users), self.templates)
        )

        # Randomize the ordering for maximum fun
        random.shuffle(users)

        if len(available_templates) == 0:
            await ctx.send("Invalid usage.")
            return

        template = random.choice(available_templates)
        # Handle any randoms
        get_best_random(users, ctx.guild.members)

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
async def on_message(message):
    if "harambe" in message.content.lower():
        emoji = "\U0001F346"
        await message.add_reaction(emoji)
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("====================")


bot.add_cog(BonoboCog(bot))
bot.run(TOKEN)
