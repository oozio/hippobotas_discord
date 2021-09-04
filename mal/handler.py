import enum
import re

from utils import discord, mal

def handle(command, cmd_input, discord_user):
    if command == 'addmal':
        return f"haven't implemented {command} yet, check back later :3"
    if command == 'mal': 
        username = cmd_input.get('mal_name')
        if not username:
            # username = mal.map_user(discord_user)
            return f"not implemented yet quq"
        result = mal.get_mal_user(username)
        return result
    return f"UNKNOWN COMMAND: {command}"
