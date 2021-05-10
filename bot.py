"""A free and open source remake of the bot from the discord server 'cup'."""

#!/usr/bin/env python

import json
import typing
from pathlib import Path

import aiosqlite
import discord.ext.commands.bot


# todo: figure out permissions and get a proper bot invite link to put in the readme
# todo: rename and recategorise config keys
# todo: add logging


__version__ = '0.2.1'


CONFIG_FILE_PATH = Path('config.json')
DB_FILE_PATH = Path('cup.db')


class CupBot(discord.ext.commands.bot.Bot):
    """Subclass of Bot which overrides on_ready and on_message, and adds specific functions."""

    def __init__(self, config: dict, *args, **kwargs):
        """Make config an attribute and declare the conn attribute, then call the superclass init."""
        self.config = config
        self.conn = None

        super().__init__(*args, **kwargs)

    async def on_ready(self):
        """Initialise the database and print a startup message."""
        self.conn = await self._init_db()
        print('Started.')

    async def _init_db(self, path: Path = None) -> aiosqlite.Connection:
        """Connect to an sql database and create tables if they do not exist.

        Args:
            path -- path to the sqlite3 database file. Will default to DB_FILE_PATH.
        Returns a database connection object.
        """
        if path is None:
            path = DB_FILE_PATH

        conn = await aiosqlite.connect(path, loop=self.loop)
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
    def _find_role(guild: discord.Guild, name: str) -> typing.Union[discord.Role, None]:
        """Search for a role with the name and return it or None if not found."""
        for role in guild.roles:
            if role.name == name:
                return role
        return None

    async def is_mug(self, message: discord.Message) -> bool:
        """Check for messages that says mug.

        Returns True if the message says 'mug', False otherwise.

        If the return value is True, it will also give the user the banished role, and write to the database that
        they have said sorry zero times.
        """
        if message.channel.name != self.config['strings']['cup_channel']:
            return False

        if message.content.casefold() == self.config['strings']['banned_word']:
            # noinspection PyTypeChecker
            banished_role = self._find_role(message.guild, self.config['strings']['banished_role'])
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
        """Check for messages that do not say cup.

        Returns False if the message says 'cup', True otherwise.

        If the return value is True, it will also send a message in the channel.
        """
        if message.channel.name != self.config['strings']['cup_channel']:
            return False

        if message.content.casefold() != self.config['strings']['allowed_word']:
            await message.channel.send(self.config['strings']['not_cup_msg'].format(mention=message.author.mention))
            return True

        return False

    async def is_sorry(self, message: discord.Message) -> bool:
        """Check for sorry messages.

        Returns True if the message is in a sorry channel and by a user that needs to say sorry, False otherwise.

        If the return value is True, it will also check the number of times the user has said sorry from the database,
        and remove their banished role if applicable.
        """
        if message.channel.name != self.config['strings']['sorry_channel']:
            return False

        # noinspection PyTypeChecker
        banished_role = self._find_role(message.guild, self.config['strings']['banished_role'])
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
                    await self.conn.execute(
                        'INSERT INTO sorry (user_id, server_id, sorry_count) VALUES (?, ?, ?)',
                        (message.author.id, message.guild.id, 0)
                    )
                    await self.conn.commit()

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
        """Process messages.

        Check for mug messages, sorry messages, and not cup messages. Then run the superclass method
        (process commands, although there aren't any regular commands at the moment).
        """
        if message.author.bot:
            return

        if await self.is_mug(message):
            return
        if await self.is_sorry(message):
            return
        await self.is_not_cup(message)

        await super().on_message(message)


def main():
    """Load config from file and start the bot."""
    with open(CONFIG_FILE_PATH, encoding='utf-8') as config_file:
        config = json.load(config_file)

    bot = CupBot(config, command_prefix='!')
    print('Starting..')
    bot.run(config['token'])


if __name__ == '__main__':
    main()
