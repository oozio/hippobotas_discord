import enum
import re

from utils import discord, mal

def handle(command, input):
    if command == 'addmal':
        return f"haven't implemented {command} yet, check back later :3"
    if command == 'mal': 
        username = input.get('mal_name')
        result = mal.get_mal_user(username)
        return f"MAL profile info for {username}:\n{result}"
    return f"UNKNOWN COMMAND: {command}"
