import datetime
import json
import os
from shutil import copyfile

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from cogs.core.config.config_botchannel import botchannel_check
from cogs.core.config.config_embedcolour import get_embedcolour
from cogs.core.config.config_general import get_defaultconfig
from cogs.core.config.config_prefix import get_prefix_string
from cogs.core.functions.automaticdelete import add_automaticdelete
from cogs.core.functions.functions import (
    get_author,
)
from cogs.core.functions.logging import log


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        time = datetime.datetime.now()
        user = ctx.author.name
        mention = ctx.author.mention
        msg = ctx.message.content
        msg2 = ctx.message
        name = ctx.channel.name
        if isinstance(error, CommandNotFound):
            return
            # out of function for verifying on top.gg
            if botchannel_check(ctx):
                embed = discord.Embed(
                    title="Fehler",
                    description='Der Befehl "' + str(msg) + '" existiert nicht!',
                    color=get_embedcolour(ctx.message),
                )
                embed.set_footer(
                    text="for "
                    + str(user)
                    + " | by "
                    + str(get_author())
                    + " | Prefix "
                    + get_prefix_string(message=ctx.message),
                    icon_url="https://media.discordapp.net/attachments/645276319311200286"
                    "/803322491480178739"
                    "/winging-easy.png?width=676&height=676",
                )
                await ctx.send(embed=embed)
                log(
                    input=str(time)
                    + ": Der Spieler "
                    + str(user)
                    + ' hat probiert den ungültigen Befehl "'
                    + str(msg)
                    + '" zu nutzen!',
                    id=ctx.guild.id,
                )
            else:
                log(
                    input=str(time)
                    + ": Der Spieler "
                    + str(user)
                    + ' hat probiert den ungültigen Befehl "'
                    + str(msg)
                    + '" zu nutzen!',
                    id=ctx.guild.id,
                )
                await ctx.send(
                    str(mention)
                    + ", dieser Befehl kann nur im Kanal #{} genutzt werden.".format(
                        channel
                    ),
                    delete_after=3,
                )
                await msg2.delete()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        path = os.path.join("data", "configs", f"{guild.id}.json")
        pathcheck = os.path.join("data", "configs", "deleted", f"{guild.id}.json")
        # config
        if os.path.isfile(pathcheck):
            copyfile(pathcheck, path)
            os.remove(pathcheck)
        else:
            with open(path, "w") as f:
                data = get_defaultconfig()
                json.dump(data, f, indent=4)
        # logs
        path = os.path.join("data", "logs", f"{guild.id}.txt")
        pathcheck = os.path.join("data", "logs", "deleted", f"{guild.id}.txt")
        if os.path.isfile(pathcheck):
            copyfile(pathcheck, path)
            os.remove(pathcheck)
        else:
            log(
                f"{datetime.datetime.now()}: Der Bot ist dem Server beigetreten.",
                guild.id,
            )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        path = os.path.join("data", "configs", f"{guild.id}.json")
        path2 = os.path.join("data", "logs", f"{guild.id}.txt")
        dest = os.path.join("data", "configs", "deleted", f"{guild.id}.json")
        dest2 = os.path.join("data", "logs", "deleted", f"{guild.id}.txt")
        copyfile(path, dest)
        copyfile(path2, dest2)
        os.remove(path)
        os.remove(path2)
        add_automaticdelete(guild.id)


########################################################################################################################


def setup(bot):
    bot.add_cog(events(bot))