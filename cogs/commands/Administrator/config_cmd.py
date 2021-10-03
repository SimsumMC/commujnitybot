import datetime
import inspect
import os

import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument

from cogs.core.config.config_autoroles import get_autorole_mentions_list
from cogs.core.config.config_botchannel import get_botchannel_obj_list
from cogs.core.config.config_buttoncolour import translate_buttoncolour, get_button_colour_list
from cogs.core.config.config_embedcolour import (
    get_embedcolour,
    colourcode_to_name,
    get_embedcolour_code,
)
from cogs.core.config.config_general import get_config
from cogs.core.config.config_memechannel import get_memechannel_obj_list
from cogs.core.config.config_prefix import get_prefix_string
from cogs.core.defaults.defaults_embed import get_embed_thumbnail, get_embed_footer
from cogs.core.functions.func_json import writejson, readjson
from cogs.core.functions.logging import log
from config import DEFAULT_PREFIX, EMBEDCOLOUR_CODES, EMBEDCOLOURS_SUPPORTED


class config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    cooldown = 5

    @commands.group(name="config", aliases=["settings", "conf", "set"])
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.config_help)

    @config.command(name="help", aliases=["hilfe, commands, befehle, cmds"])
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_help(self, ctx):
        prefix = await get_prefix_string(ctx.message)
        time = datetime.datetime.now()
        user = ctx.author.name
        embed = discord.Embed(
            title="**Config Hilfe**",
            description=f"Hier findest du alle Subbefehle zum {prefix} config Befehl!",
            colour=await get_embedcolour(ctx.message),
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        embed.add_field(
            name=f"**{prefix}config prefix <Präfix>**",
            value="Ändere den Prefix deines Bots!",
            inline=False,
        )
        embed.add_field(
            name=f'**{prefix}config colour <Embed / Button> <Farbe ({prefix}colours / "random")>**',
            value="Ändere die Farbe der Embeds!",
            inline=False,
        )
        embed.add_field(
            name=f"**{prefix}config botchannel add/remove <@channel>**",
            value="Sorge dafür das die Befehle nur in einem bestimmten Kanal funktionieren!",
            inline=False,
        )
        embed.add_field(
            name=f"**{prefix}config memechannel add/remove <@channel>**",
            value="Sorge dafür das der Meme Befehl nur in einem bestimmten Kanal funktioniert!",
            inline=False,
        )
        embed.add_field(
            name=f'**{prefix}config memesource <Reddit Name / "default">**',
            value="Sorge dafür das der Meme Befehl nur in einem bestimmten Kanal funktioniert!",
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            text=str(time)
                 + ": Der Nutzer "
                 + str(user)
                 + " hat den Befehl "
                 + prefix
                 + "config hilfe benutzt.",
            guildid=ctx.guild.id,
        )

    @config.command(name="show", aliases=["werte", "s", "all"])
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_show(self, ctx):
        time = datetime.datetime.now()
        user = ctx.author.name
        embed = discord.Embed(
            title="**Config Show**",
            description=f"Hier findest du die Konfiguration deines Servers!",
            colour=await get_embedcolour(ctx.message),
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        config_json = await get_config(guildid=ctx.guild.id)
        embed.add_field(name="**Prefix**", value=config_json["prefix"], inline=False)
        embed.add_field(
            name="**Embed-Farbe**",
            value=await colourcode_to_name(config_json["embedcolour"]),
            inline=False,
        )
        embed.add_field(
            name="**Button-Farbe**",
            value=await translate_buttoncolour(language="de", colour=config_json["buttoncolour"]),
            inline=False,
        )
        embed.add_field(name="**Blacklist**", value="a!blacklist list", inline=False)
        embed.add_field(name="**Triggerlist**", value="a!trigger list", inline=False)
        embed.add_field(
            name="**Botchannel**",
            value=str(await get_botchannel_obj_list(ctx))
            if await get_botchannel_obj_list(ctx)
            else "Nicht definiert",
            inline=False,
        )
        embed.add_field(
            name="**Memechannel**",
            value=str(await get_memechannel_obj_list(ctx))
            if await get_memechannel_obj_list(ctx)
            else "Nicht definiert",
            inline=False,
        )
        embed.add_field(
            name="**Autoroles**",
            value=await get_autorole_mentions_list(guild=ctx.guild),
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            text=str(time)
                 + ": Der Nutzer "
                 + str(user)
                 + " hat den Befehl "
                 + await get_prefix_string(ctx.message)
                 + "config hilfe benutzt.",
            guildid=ctx.guild.id,
        )

    @config.command(name="prefix", aliases=["präfix"])
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_prefix(self, ctx, arg=DEFAULT_PREFIX):
        prefix = await get_prefix_string(ctx.message)
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        if prefix == arg:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Der Präfix muss sich vom aktuellen unterscheiden!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}config prefix versucht den Prefix zum aktuellen Wert zu ändern! ",
                ctx.guild.id,
            )
            return
        elif len(arg) > 16:
            embed = discord.Embed(
                title="**Fehler**",
                description=f'Der Präfix darf maximal 16 Zeichen lang sein, daher ist dein eingegebener Präfix "`{arg}`" ungültig.',
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}config prefix versucht den Prefix zu ändern, der eingegebene Wert war aber länger als 16 Zeichen ({len(arg)})! ",
                ctx.guild.id,
            )
            return
        await writejson(key="prefix", value=[str(arg)], path=path)
        embed = discord.Embed(
            title="**Config Prefix**", colour=await get_embedcolour(ctx.message)
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        embed.add_field(
            name="‎",
            value=f"Der Prefix wurde erfolgreich zu ```{arg}``` geändert.",
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}"
            f'config den Prefix zu "{arg}" geändert!',
            guildid=ctx.guild.id,
        )

    @config.group(
        name="colour", aliases=["farbe", "color", "farben"], usage="<set / list>"
    )
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour(self, ctx):
        if ctx.invoked_subcommand is None:
            class error(inspect.Parameter):
                name = "config colour"
                param = "subcommand"

            raise MissingRequiredArgument(error)

    @config_colour.group(
        name="embed", aliases=["msg", "message", "nachricht"], usage="<set / list>"
    )
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour_embed(self, ctx):
        if ctx.invoked_subcommand is None:
            class error(inspect.Parameter):
                name = "config colour embed"
                param = "subcommand"

            raise MissingRequiredArgument(error)

    @config_colour_embed.command(name="set", aliases=["s"], usage="<Farbe>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour_embed_set(self, ctx, colour):
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        if colour.lower() not in EMBEDCOLOURS_SUPPORTED:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Die Farbe ```{str(colour.lower()).capitalize()}``` existiert nicht!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat versucht den Befehl {await get_prefix_string(ctx.message)}config colour embed set zu benutzen, hat aber eine ungütige Farbe angegeben!",
                ctx.guild.id,
            )
            return
        await writejson(
            key="embedcolour",
            value=await get_embedcolour_code(colour.lower()),
            path=path,
        )
        embed = discord.Embed(
            title="**Config Colour**",
            description=f"Die Embed-Farbe wurde nun zu ```{str(colour.lower()).capitalize()}``` geändert!",
            colour=await get_embedcolour(ctx.message),
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {await get_prefix_string(ctx.message)}"
            f"config colour embed set die Farbe zu {str(colour.lower()).capitalize()} geändert!",
            guildid=ctx.guild.id,
        )

    @config_colour_embed.command(name="list", aliases=["l", "all"])
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour_embed_list(self, ctx):
        time = datetime.datetime.now()
        user = ctx.author.name
        colours = "".join([colour.capitalize() + ", " for colour in EMBEDCOLOUR_CODES])[
                  :-2
                  ]
        embed = discord.Embed(
            title="**Config Colour**",
            description=colours,
            colour=await get_embedcolour(ctx.message),
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat den Befehl {await get_prefix_string(ctx.message)}"
            "config colour embed list benutzt!",
            guildid=ctx.guild.id,
        )

    @config_colour.group(
        name="button", aliases=["knopf", "b"], usage="<set / list>"
    )
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour_button(self, ctx):
        if ctx.invoked_subcommand is None:
            class error(inspect.Parameter):
                name = "config colour button"
                param = "subcommand"

            raise MissingRequiredArgument(error)

    @config_colour_button.command(name="set", aliases=["s"], usage="<Farbe>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour_button_set(self, ctx, colour):
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        if colour.lower() in await get_button_colour_list("en"):
            buttoncolour = colour.lower()
        elif colour.lower() in await get_button_colour_list("de"):
            buttoncolour = await translate_buttoncolour(language="en", colour=colour.lower())
        else:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Die Farbe ```{str(colour.lower()).capitalize()}``` existiert nicht!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat versucht den Befehl {await get_prefix_string(ctx.message)}config colour button set zu benutzen, hat aber eine ungütige Farbe angegeben!",
                ctx.guild.id,
            )
            return
        await writejson(key="buttoncolour", value=str(buttoncolour),
                        path=path)
        embed = discord.Embed(
            title="**Config Colour**",
            description=f"Die Button-Farbe wurde nun zu ```{str(colour.lower()).capitalize()}``` geändert!",
            colour=await get_embedcolour(ctx.message),
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {await get_prefix_string(ctx.message)}"
            f"config colour button set die Button-Farbe zu {str(colour.lower()).capitalize()} geändert!",
            guildid=ctx.guild.id,
        )

    @config_colour_button.command(name="list", aliases=["l", "all"])
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_colour_button_list(self, ctx):
        time = datetime.datetime.now()
        user = ctx.author.name
        colours = "".join([colour.capitalize() + ", " for colour in await get_button_colour_list("de")])[
                  :-2
                  ]
        embed = discord.Embed(
            title="**Config Colour**",
            description=colours,
            colour=await get_embedcolour(ctx.message),
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat den Befehl {await get_prefix_string(ctx.message)}"
            "config colour button list benutzt!",
            guildid=ctx.guild.id,
        )

    @config.group(name="botchannel", aliases=["bot"], usage="add/remove <@Channel>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_botchannel(self, ctx):
        if ctx.invoked_subcommand is None:
            class error(inspect.Parameter):
                name = "config botchannel"
                param = "subcommand"

            raise MissingRequiredArgument(error)

    @config_botchannel.command(name="add", aliases=["hinzufügen"], usage="<@Channel>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    async def config_botchannel_add(self, ctx, channel: discord.TextChannel):
        prefix = await get_prefix_string(ctx.message)
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        botchannel = await readjson(key="botchannel", path=path)
        if channel.id in botchannel:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Der Channel {channel.mention} ist breits auf der Botchannel-Liste!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}config botchannel add versucht den bereits vorhandenen Channel {channel.name} auf die Botchannel-Liste hinzuzufügen!",
                ctx.guild.id,
            )
            return
        await writejson(key="botchannel", value=channel.id, path=path, mode="append")
        embed = discord.Embed(
            title="**Config Botchannel**", colour=await get_embedcolour(ctx.message)
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        embed.add_field(
            name="‎",
            value=f"Der Channel ```{channel.name}``` wurde erfolgreich zu der Botchannel-Liste hinzugefügt.",
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}"
            f'botchannel add den Channel "{channel.name}" zu der Botchannel-Liste hinzugefügt.',
            guildid=ctx.guild.id,
        )

    @config_botchannel.command(name="remove", aliases=["entfernen"], usage="<@Channel>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    async def config_botchannel_remove(self, ctx, channel: discord.TextChannel):
        prefix = await get_prefix_string(ctx.message)
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        botchannel = await readjson(key="botchannel", path=path)
        if channel.id not in botchannel:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Der Channel {channel.mention} ist nicht auf der Memechannel-Liste vorhanden!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}config memechannel versucht den nicht gesetzten Channel {channel.name} auf die Memechannel-Liste zu packen!",
                ctx.guild.id,
            )
            return
        await writejson(key="botchannel", value=channel.id, path=path, mode="remove")
        embed = discord.Embed(
            title="**Config Botchannel**", colour=await get_embedcolour(ctx.message)
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        embed.add_field(
            name="‎",
            value=f"Der Channel ```{channel.name}``` wurde erfolgreich von der Memechannel-Liste entfernt.",
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}"
            f'memechannel remove den Channel "{channel.name}" von der Memechannel-Liste entfernt.',
            guildid=ctx.guild.id,
        )

    @config.group(name="memechannel", aliases=["meme"], usage="add/remove <@channel>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def config_memechannel(self, ctx):
        if ctx.invoked_subcommand is None:
            class error(inspect.Parameter):
                name = "config memechannel"
                param = "subcommand"

            raise MissingRequiredArgument(error)

    @config_memechannel.command(name="add", aliases=["hinzufügen"], usage="<@Channel>")
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    async def config_memechannel_add(self, ctx, channel: discord.TextChannel):
        prefix = await get_prefix_string(ctx.message)
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        memechannel = await readjson(key="botchannel", path=path)
        if channel.id in memechannel:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Der Channel {channel.mention} ist breits auf der Memechannel-Liste!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}config memechannel add versucht den bereits vorhandenen Channel {channel.name} auf die Memechannel-Liste hinzuzufügen!",
                ctx.guild.id,
            )
            return
        await writejson(key="memechannel", value=channel.id, path=path, mode="append")
        embed = discord.Embed(
            title="**Config Memechannel**", colour=await get_embedcolour(ctx.message)
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        embed.add_field(
            name="‎",
            value=f"Der Channel ```{channel.name}``` wurde erfolgreich zu der Memechannel-Liste hinzugefügt.",
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}"
            f'memechannel add den Channel "{channel.name}" zu der Memechannel-Liste hinzugefügt.',
            guildid=ctx.guild.id,
        )

    @config_memechannel.command(
        name="remove", aliases=["entfernen"], usage="<@Channel>"
    )
    @commands.cooldown(1, cooldown, commands.BucketType.guild)
    async def config_memechannel_remove(
            self, ctx: commands.Context, channel: discord.TextChannel
    ):
        prefix = await get_prefix_string(ctx.message)
        time = datetime.datetime.now()
        user = ctx.author.name
        path = os.path.join("data", "configs", f"{ctx.guild.id}.json")
        memechannel = await readjson(key="memechannel", path=path)
        if channel.id not in memechannel:
            embed = discord.Embed(
                title="**Fehler**",
                description=f"Der Channel {channel.mention} ist nicht auf der Memechannel-Liste vorhanden!",
                colour=await get_embedcolour(ctx.message),
            )
            embed._footer = await get_embed_footer(ctx)
            embed._thumbnail = await get_embed_thumbnail()
            await ctx.send(embed=embed)
            await log(
                f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}config memechannel versucht den nicht gesetzten Channel {channel.name} auf die Memechannel-Liste zu packen!",
                ctx.guild.id,
            )
            return
        await writejson(key="memechannel", value=channel.id, path=path, mode="remove")
        embed = discord.Embed(
            title="**Config Memechannel**", colour=await get_embedcolour(ctx.message)
        )
        embed._footer = await get_embed_footer(ctx)
        embed._thumbnail = await get_embed_thumbnail()
        embed.add_field(
            name="‎",
            value=f"Der Channel ```{channel.name}``` wurde erfolgreich von der Memechannel-Liste entfernt.",
            inline=False,
        )
        await ctx.send(embed=embed)
        await log(
            f"{time}: Der Nutzer {user} hat mit dem Befehl {prefix}"
            f'memechannel remove den Channel "{channel.name}" von der Memechannel-Liste entfernt.',
            guildid=ctx.guild.id,
        )


########################################################################################################################


def setup(bot):
    bot.add_cog(config(bot))
