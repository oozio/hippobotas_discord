import enum
import re

from utils import discord, mal

def handle(command, cmd_input, discord_user):
    if command == 'addmal':
        mal_username = cmd_input.get('mal_name')
        return mal.set_mal_user(discord_user, mal_username)
    if command == 'mal': 
        mal_username = cmd_input.get('mal_name')
        # if not username:
        mal_username = mal.map_user(discord_user)
            # return f"not implemented yet quq"
        result = mal.get_mal_user(mal_username)
        return result
    return f"UNKNOWN COMMAND: {command}"
