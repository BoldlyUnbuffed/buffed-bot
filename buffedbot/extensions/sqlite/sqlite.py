import aiosqlite

from discord.ext import commands
from asyncio import gather
from aiopath import PurePath, AsyncPath


def dict_compact(dict):
    return {k: dict[k] for k in dict if dict[k] != None}


def get_column_names(dict, /, wrap_brackets=True):
    key_list = ",".join(dict.keys())
    if not wrap_brackets:
        return key_list
    return f"({key_list})"


def get_placeholder_names(dict):
    return f'({(",".join([f":{k}" for k in dict]))})'


def get_placeholder_values(dict):
    return tuple(dict.values())


DB_FILENAME = "sqlite.db"


class SQLite(commands.Cog, name="sqlite"):
    def __init__(self, bot):
        self.bot = bot

    def get_ctx_db(self, ctx):
        if not ctx.guild:
            return self.db
        return self.get_guild_db(ctx.guild)

    def get_guild_db(self, guild):
        if not guild:
            raise commands.NoPrivateMessage()
        if not guild.id in self.guild_dbs:
            raise commands.GuildNotFound(guild)
        return self.guild_dbs[guild.id]

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Ensure guild path was created
        await self.bot.get_cog("guildstorage").create_guild_storage(guild)
        self.guild_dbs[guild.id] = await self.connect_guild_db(guild)

    async def on_guild_remove(self, guild):
        if guild.id in self.guild_dbs:
            await self.guild_dbs[guild.id].close()
            await AsyncPath(self.get_guild_db_path(guild)).unlink()

    async def cog_load(self):
        self.db = await aiosqlite.connect(DB_FILENAME)

        dbs = await gather(*[self.connect_guild_db(guild) for guild in self.bot.guilds])
        self.guild_dbs = dict(zip([guild.id for guild in self.bot.guilds], dbs))

    async def cog_unload(self):
        await self.db.close()
        await gather(*[self.guild_dbs[db].close() for db in self.guild_dbs])

    def get_guild_db_path(self, guild):
        guild_storage_path = self.bot.get_cog("guildstorage").get_guild_storage_path(
            guild
        )
        return str(PurePath(guild_storage_path, DB_FILENAME))

    async def connect_guild_db(self, guild):
        return await aiosqlite.connect(self.get_guild_db_path(guild))


async def setup(bot):
    await bot.get_cog("system").load_extension("guildstorage")
    await bot.add_cog(SQLite(bot))


async def teardown(bot):
    await bot.remove_cog("SQLite")
