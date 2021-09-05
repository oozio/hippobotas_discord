import json
import random

from enum import Enum

from utils import http, dynamodb

# from common.utils import find_true_name
import constants.steam as const
from constants.steam import DynamoDBInfo


def get_steam_user(username):
    # pulls info from steam for a given username
    url = f"{const.JIKAN_API}/user/{username}"
    user_data = http.make_request('get', url)
    if not user_data:
        raise ValueError(f"No user data found for {username}")
    user = const.User(user_data)

    result = {
        'content': "",
        "embed": user.format_for_embed()
    }
    return result

def map_user(discord_user):
    # returns whichever steam username is connected with <discord_user>
    response = dynamodb.get_rows(DynamoDBInfo.TABLE.value, DynamoDBInfo.PK_TEMPLATE.value.format(discord_user))
    if not response:
        raise ValueError(f"No associated steam user found for you (<@{discord_user}>), run /addsteam <steam username> to set")
    # there should only be one row
    assert(len(response) == 1)
    return response[0][DynamoDBInfo.USER_COLUMN.value]

def set_steam_user(discord_user, steam_user):
    # check that <steam_user> is valid
    result = get_steam_user(steam_user)

    pk_value = DynamoDBInfo.PK_TEMPLATE.value.format(discord_user)
    new_column = {
        DynamoDBInfo.USER_COLUMN.value: steam_user
    }
    dynamodb.set_rows(DynamoDBInfo.TABLE.value, pk_value, new_column)
    
    result['content'] = f"set <@{discord_user}>'s steam to [{steam_user}](https://myanimelist.net/profile/{steam_user})"

    return result