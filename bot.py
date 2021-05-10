#!/usr/bin/env python

import json
import typing
from pathlib import Path

import aiosqlite
import discord.ext.commands.bot


__version__ = '0.2.0a'


CONFIG_FILE_PATH = Path('config.json')
DB_FILE_PATH = Path('cup.db')


class CupBot(discord.ext.commands.bot.Bot):
    def __init__(self, config: dict, *args, **kwargs):
        self.config = config
        self.conn = None

        super().__init__(*args, **kwargs)

    async def on_ready(self):
        self.conn = await self.init_db()
        print('Started.')

    async def init_db(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(DB_FILE_PATH, loop=self.loop)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS sorry (
            user_id INT,
            server_id INT,
            sorry_count INT,
            PRIMARY KEY (user_id, server_id)
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS cups (
            user_id INT PRIMARY KEY,
            cups_count INT,
            legendary_cups_count INT
        );
        """)
        await conn.commit()

        return conn

    @staticmethod
    def find_role(guild: discord.Guild, name: str) -> typing.Union[discord.Role, None]:
        for role in guild.roles:
            if role.name == name:
                return role
        return None

    async def is_mug(self, message: discord.Message):
        if message.channel.name != self.config['strings']['cup_channel']:
            return False

        if message.content.casefold() == self.config['strings']['banned_word']:
            # noinspection PyTypeChecker
            banished_role = self.find_role(message.guild, self.config['strings']['banished_role'])
            if banished_role:
                await message.author.add_roles(banished_role, reason='mug')
            return True

        return False

    async def is_not_cup(self, message: discord.Message):
        if message.channel.name != self.config['strings']['cup_channel']:
            return False

        if message.content.casefold() != self.config['strings']['allowed_word']:
            await message.channel.send(self.config['strings']['not_cup_msg'].format(mention=message.author.mention))
            return True

        return False

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not await self.is_mug(message):
            await self.is_not_cup(message)

        await super().on_message(message)


def main():
    with open(CONFIG_FILE_PATH, encoding='utf-8') as config_file:
        config = json.load(config_file)

    bot = CupBot(config, command_prefix='!')
    print('Starting..')
    bot.run(config['token'])


if __name__ == '__main__':
    main()
