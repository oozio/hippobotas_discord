import boto3
import re
import requests

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

MAX_RESPONSE_LENGTH = 2000

RESPONSE_TYPES =  {
                    "PONG": 1,
                    "ACK_NO_SOURCE": 2,
                    "MESSAGE_NO_SOURCE": 3,
                    "MESSAGE_WITH_SOURCE": 4,
                    "ACK_WITH_SOURCE": 5
                  }

BASE_URL = "https://discord.com/api/v8"

ssm = boto3.client('ssm', region_name='us-east-2')

PUBLIC_KEY = ssm.get_parameter(Name="/discord/public_key", WithDecryption=True)['Parameter']['Value']
BOT_TOKEN = ssm.get_parameter(Name="/discord/bot_token", WithDecryption=True)['Parameter']['Value']
HEADERS = {
    "Authorization": f"Bot {BOT_TOKEN}",
    "Content-Type": "application/json"
}

SIZE_ROLE_NAME_PATTERN = re.compile(r'Size (?P<size>\d+)')

_PERMISSIONS = {
    "VIEW_AND_USE_SLASH_COMMANDS": 0x0080000400,
    "ADD_REACTIONS": 0x0000000040,
    "USE_EXTERNAL_EMOJIS": 0x0000040000,
    "SEND_MESSAGES": 0x0000000800
}

def _form_permission():
    result = 0
    for permission in _PERMISSIONS.values():
        result = result | permission
    return result

_ROLES_CACHE = {}
def _get_all_roles(server_id, force_refresh=False):
    if server_id in _ROLES_CACHE and not force_refresh:
        return _ROLES_CACHE[server_id]
    url = f"{BASE_URL}/guilds/{server_id}/roles"
    roles = requests.get(url, headers=HEADERS).json()
    _ROLES_CACHE[server_id] = roles
    return roles

def get_roles_by_ids(server_id, role_ids):
    roles = _get_all_roles(server_id)
    return [role for role in roles if role['id'] in role_ids]

def get_roles_by_names(server_id, role_names):
    roles = _get_all_roles(server_id)
    return [role for role in roles if role['name'] in role_names]

def _get_role_ids_by_name(server_id, role_names):
    results = {key: None for key in role_names}
    for role in _get_all_roles(server_id):
        if role['name'] in role_names:
            results[ role['name'] ] = role['id']
        if None not in results.values():
            return results

def _get_role_names_by_id(server_id, role_ids):
    results = {key: None for key in role_ids}
    for role in _get_all_roles(server_id):
        if role['id'] in role_ids:
            results[ role['id'] ] = role['name']
        if None not in results.values():
            return results

def remove_role(user_id, role_id, server_id):
    url = f"{BASE_URL}/guilds/{server_id}/members/{user_id}/roles/{role_id}"
    requests.delete(url, headers=HEADERS)

def add_role(user_id, role_id, server_id):
    url = f"{BASE_URL}/guilds/{server_id}/members/{user_id}/roles/{role_id}"
    requests.put(url, headers=HEADERS)

def get_user_roles(server_id, user_id):
    url = f"{BASE_URL}/guilds/{server_id}/members/{user_id}"
    user = requests.get(url,  headers=HEADERS).json()
    print(f'user: {user}')
    return get_roles_by_ids(server_id, user['roles'])

def get_all_users(server_id):
    # return all user_ids in a server

    # idk if this works? my bot is broken :(
    # https://discord.com/developers/docs/resources/guild#list-guild-members
    url = f"{BASE_URL}/guilds/{server_id}/members?limit=1000"
    response = requests.get(url,  headers=HEADERS)
    return response.json()

def change_role(server_id, user_id, old_role_name, new_role_name):
    role_ids_by_name = _get_role_ids_by_name(server_id, [new_role_name, old_role_name])
    remove_role(user_id, role_ids_by_name[old_role_name], server_id)
    add_role(user_id, role_ids_by_name[new_role_name], server_id)

_LOADED_SERVERS = set()
_ALL_CHANNELS_BY_ID = {}
_CHANNELS_BY_NAME_AND_SERVER = {}

def _load_channels(server_id, force_refresh=False):
    if server_id in _LOADED_SERVERS and not force_refresh:
        return
    url = f'{BASE_URL}/guilds/{server_id}/channels'
    channels = requests.get(url, headers=HEADERS).json()
    _ALL_CHANNELS_BY_ID.update({channel['id']: channel for channel in channels})
    _CHANNELS_BY_NAME_AND_SERVER.update({
            (channel['name'], channel['guild_id']): channel
            for channel in channels
    })
    _LOADED_SERVERS.add(server_id)

def get_channel_by_id(channel_id):
    """ Returns a channel object.

    returns channel object (dict).
    Params found at https://discord.com/developers/docs/resources/channel
    """
    if channel_id in _ALL_CHANNELS_BY_ID:
        return _ALL_CHANNELS_BY_ID[channel_id]

    url = f"https://discord.com/api/v8/channels/{channel_id}"
    channel = requests.get(url, headers=HEADERS).json()
    _load_channels(channel['guild_id'])
    return channel

def get_channel(channel_name, server_id):
    """ Returns a channel object.

    returns channel object (dict).
    Params found at https://discord.com/developers/docs/resources/channel
    """
    _load_channels(server_id)
    return _CHANNELS_BY_NAME_AND_SERVER[channel_name, server_id]

def set_channel_permissions(role_id, channel_name, server_id, grant_type):
    """ Sets a channel's permissions for a given role.

    permissions found at https://discord.com/developers/docs/topics/permissions#permissions])
    """
    channel_id = _CHANNELS_BY_NAME_AND_SERVER[channel_name, server_id]['id']
    permissions = _form_permission()

    put_body = {
        "type": 0, # roles
        grant_type: permissions
    }

    url = f"{BASE_URL}/channels/{channel_id}/permissions/{role_id}"

    requests.put(url, json=put_body, headers=HEADERS)

def move_user_to_channel(server_id, user_id, channel_name):
    # only works for voice channels
    body = {
        "channel_id": _CHANNELS_BY_NAME_AND_SERVER[channel_name, server_id]['id']
    }

    url = f"{BASE_URL}/guilds/{server_id}/members/{user_id}"
    requests.patch(url, json=body, headers=HEADERS)

def post_message_in_channel(channel_id, content):
    url = f'{BASE_URL}/channels/{channel_id}/messages'
    body = {'content': content}
    requests.post(url, json=body, headers=HEADERS)

def get_messages(channel_id, limit, specified_message):
    # gets the last <limit> messages from the specified channel, and appends any message specified by id
    # doesn't check if <specified_message> is duplicated
    url = f"https://discord.com/api/v8/channels/{channel_id}/messages?limit={limit}"
    ind_url = f"https://discord.com/api/v8/channels/{channel_id}/messages/{specified_message}"
    messages = requests.get(url, headers=HEADERS).json()
    if specified_message:
        messages.append(requests.get(ind_url, headers=HEADERS).json())

    return messages

def _verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts  = event['params']['header'].get('x-signature-timestamp')
    message = auth_ts.encode() + raw_body.encode()

    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(message, bytes.fromhex(auth_sig))
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

def _ping_pong(body):
    if body.get("type") == 1:
        return True
    return False

def check_input(event):
    _verify_signature(event)
    body = event.get('body-json')
    if _ping_pong(body):
        return format_response("PONG", None)

def get_input(data, target):
    for option in data.get('options', []):
        if option['name'] == target:
            return option['value']

def format_response(content, ephemeral, response_type=None):
    if response_type == 'PONG':
        return {
        "type": RESPONSE_TYPES[response_type] if response_type in RESPONSE_TYPES else RESPONSE_TYPES['MESSAGE_WITH_SOURCE'],
        }

    response = {
            "content": content,
            "embeds": [],
            "allowed_mentions": [],
            "flags": 64 if ephemeral else None
        }

    return response

def send_followup(application_id, interaction_token, content, ephemeral=False):
    while len(content) > MAX_RESPONSE_LENGTH:
        send_followup(application_id, interaction_token, content[:MAX_RESPONSE_LENGTH])
        content = content[MAX_RESPONSE_LENGTH:]

    body = format_response(content, ephemeral=ephemeral)
    url = f"{BASE_URL}/webhooks/{application_id}/{interaction_token}"
    requests.post(url, json=body, headers=HEADERS)

def update_response(application_id, interaction_token, content, ephemeral=False):
    remaining = ''
    if len(content) > MAX_RESPONSE_LENGTH:
        content, remaining = content[:MAX_RESPONSE_LENGTH], content[MAX_RESPONSE_LENGTH:]

    body = format_response(content, ephemeral=ephemeral)
    url = f"{BASE_URL}/webhooks/{application_id}/{interaction_token}/messages/@original"
    requests.patch(url, json=body, headers=HEADERS)

    if remaining:
        send_followup(application, interaction_token, remaining)

def delete_response(application_id, interaction_token):
    url = f"{BASE_URL}/webhooks/{application_id}/{interaction_token}/messages/@original"
    requests.delete(url, headers=HEADERS)
    
def send_response(channel_id, content, embed=None):
    response = {
        "content": content,
        "allowed_mentions": {
            # "users": [user_id]        
            }
        }
        
    if embed:
        response['embed'] = {
            "title": f"{embed.get('title')}",
            "description": f"{embed.get('description')}"
         }
         
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    response = requests.post(url, json=response, headers=HEADERS)
    
    return response

def edit_message(channel_id, message_id, content, embed={}):
    response = {
        "content": content
    }
    if embed:
        response['embed'] = {
            "title": f"{embed.get('title')}",
            "description": f"{embed.get('description')}"
         }
    url = f"{BASE_URL}/channels/{channel_id}/messages/{message_id}"
    response = requests.patch(url, json=response, headers=HEADERS)


