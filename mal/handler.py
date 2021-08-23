import enum
import re

from utils import discord, mal

def handle(command, input):
    if command == 'addmal':
        return f"haven't implemented {command} yet, check back later :3"
    if command == 'mal': 
        return mal.get_mal_user(input.get('mal_name'))
    
    return f"UNKNOWN COMMAND: {command}"
