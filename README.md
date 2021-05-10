# cup
A free and open source remake of the bot from the discord server 'cup'.

Implemented in [Python 3](https://python.org) with [discord.py](https://discordpy.readthedocs.io) and [aiosqlite](https://aiosqlite.omnilib.dev) (sqlite3 database).

## Credit

All credit for concept goes to the creator or the original discord server and bot, Wes#2394    
Original server: https://discord.gg/x3RKd5QFB8

## Features
- [x] You are only allowed to say **cup** in this server. (Send a message if a message other than cup is said in a designated channel)
- [x] If the word mug is said, give the user a 'banished' role.
- [x] A user with a banished role has to say sorry five times in a specific channel to get the banished role removed
- [x] Use the 'cups' command to get cups and legendary cups (on a cooldown) and see how many cups and legendary cups you have
- [ ] Use the 'config' command to change settings like the banned word (not in original bot)

## Run the bot yourself

- Copy config.template.json to make config.json
- [Create a discord bot account](https://discordpy.readthedocs.io/en/latest/discord.html) and fill in your token in config.json
- Install dependencies from requirements.txt with pip
- Run with python

## Add my official instance of the bot to your server

https://discord.com/api/oauth2/authorize?client_id=841017008858071133&permissions=268446720&scope=bot    
Make sure to put it high up enough in the roles list that it can manage the 'banished' role.    
Also make sure it has access to the banished channel.

## Join the official discord server
https://discord.gg/cdrgtpWhCX
