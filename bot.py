#!/usr/bin/env python

import json
import typing
from pathlib import Path

import aiosqlite
import discord.ext.commands.bot


__version__ = '0.2.0'


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

    async def is_mug(self, message: discord.Message) -> bool:
        if message.channel.name != self.config['strings']['cup_channel']:
            return False

        if message.content.casefold() == self.config['strings']['banned_word']:
            # noinspection PyTypeChecker
            banished_role = self.find_role(message.guild, self.config['strings']['banished_role'])
            if banished_role:
                await message.author.add_roles(banished_role, reason='mug')
                await self.conn.execute(
                    'REPLACE INTO sorry (user_id, server_id, sorry_count) VALUES (?, ?, ?)',
                    (message.author.id, message.guild.id, 0)
                )
                await self.conn.commit()
            return True

        return False

    async def is_not_cup(self, message: discord.Message) -> bool:
        if message.channel.name != self.config['strings']['cup_channel']:
            return False

        if message.content.casefold() != self.config['strings']['allowed_word']:
            await message.channel.send(self.config['strings']['not_cup_msg'].format(mention=message.author.mention))
            return True

        return False

    async def is_sorry(self, message: discord.Message) -> bool:
        if message.channel.name != self.config['strings']['sorry_channel']:
            return False

        # noinspection PyTypeChecker
        banished_role = self.find_role(message.guild, self.config['strings']['banished_role'])
        if message.content.casefold() == self.config['strings']['sorry_word']:
            # noinspection PyTypeChecker
            if banished_role in message.author.roles:
                cur = await self.conn.execute(
                    'SELECT sorry_count FROM sorry WHERE user_id=? AND server_id=?',
                    (message.author.id, message.guild.id)
                )
                result = await cur.fetchone()
                try:
                    sorry_count = result[0]
                except TypeError:
                    sorry_count = 0

                sorry_count_required = self.config['settings']['sorry_count_required']

                if sorry_count >= sorry_count_required:
                    await message.author.remove_roles(banished_role, reason='sorry')
                else:
                    sorry_count += 1
                    await self.conn.execute(
                        'UPDATE sorry SET sorry_count=? WHERE user_id=? AND server_id=?',
                        (sorry_count, message.author.id, message.guild.id)
                    )
                    await self.conn.commit()

        return False

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if await self.is_mug(message):
            return
        if await self.is_sorry(message):
            return
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
