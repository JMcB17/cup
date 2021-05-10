#!/usr/bin/env python

import json
import typing
from pathlib import Path

import discord.ext.commands.bot


__version__ = '0.1.0'


CONFIG_FILE_PATH = Path('config.json')


class CupBot(discord.ext.commands.bot.Bot):
    def __init__(self, config: dict, *args, **kwargs):
        self.config = config

        super().__init__(*args, **kwargs)

    # noinspection PyMethodMayBeStatic
    async def on_ready(self):
        print('Started.')

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
