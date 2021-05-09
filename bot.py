#!/usr/bin/env python

import json
from pathlib import Path
import discord.ext.commands.bot


CONFIG_FILE_PATH = Path('config.json')


class CupBot(discord.ext.commands.bot.Bot):
    def __init__(self, config: dict, *args, **kwargs):
        self.config = config
        super().__init__(*args, **kwargs)

    # noinspection PyMethodMayBeStatic
    async def on_ready(self):
        print('Started.')

    async def is_mug(self, message: discord.Message):
        # todo: implement
        return False

    async def is_not_cup(self, message: discord.Message):
        if message.content.casefold() != 'cup':
            await message.channel.send(self.config['strings']['not_cup_msg'].format(mention=message.author.mention))

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
