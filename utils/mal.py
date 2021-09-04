import json
import random

from enum import Enum

from utils import http, dynamodb


# from common.utils import find_true_name
import constants.mal as const

def check_mal_nsfw(medium, series):
    url = f"{const.JIKAN_API}/{medium}/{series}"
    series_data = http.make_request('get', url)
    for genre in series_data['genres']:
        if genre['mal_id'] == const.MAL_GENRES.HENTAI:
            return True
    return False

def get_mal_user(username, retries=5):
    # pulls info from JIKAN/MAL for a given MAL username
    url = f"{const.JIKAN_API}/user/{username}"
    user_data = http.make_request('get', url)
    user = const.User(user_data)

    result = user.format_for_embed()

    return result

def map_user(discord_user):
    # returns whichever MAL username is connected with <discord_user>
    pass

def set_mal_user(mal_user):
    user_data = 


def show_mal_user(username):
    pass
#     userdata = await get_mal_user(username)
#     if userdata:
#         # Set image
#         img_url = const.IMG_NOT_FOUND
#         if userdata['image_url']:
#             img_url = userdata['image_url']
#         img_uhtml = gen_uhtml_img_code(img_url, height_resize=100, width_resize=125)

#         # Set favorite series
#         top_series_uhtml = {'anime': (), 'manga': ()}
#         for medium in top_series_uhtml:
#             top_series = 'None'
#             top_series_url = ''
#             top_series_img = const.IMG_NOT_FOUND

#             fav_series = userdata['favorites'][medium]
#             while fav_series:
#                 rand_fav = random.choice(fav_series)
#                 is_nsfw = await check_mal_nsfw(medium, rand_fav['mal_id'])
#                 if is_nsfw:
#                     fav_series.remove(rand_fav)
#                 else:
#                     top_series = rand_fav['name']
#                     top_series_url = rand_fav['url']
#                     top_series_img = rand_fav['image_url']
#                     break

#             top_series_uhtml[medium] = (top_series, top_series_url,
#                                         gen_uhtml_img_code(top_series_img, height_resize=64))

#         user_info = UserInfo(userdata['username'], userdata['url'], 'mal')
#         kwargs = {'profile_pic': img_uhtml,
#                   'anime_completed': userdata['anime_stats']['completed'],
#                   'anime_watching': userdata['anime_stats']['watching'],
#                   'ep_watched': userdata['anime_stats']['episodes_watched'],
#                   'anime_score': userdata['anime_stats']['mean_score'],
#                   'manga_completed': userdata['manga_stats']['completed'],
#                   'manga_reading': userdata['manga_stats']['reading'],
#                   'chp_read': userdata['manga_stats']['chapters_read'],
#                   'manga_score': userdata['manga_stats']['mean_score'],
#                   'anime_img': top_series_uhtml['anime'][2],
#                   'manga_img': top_series_uhtml['manga'][2],
#                   'anime_link': top_series_uhtml['anime'][1],
#                   'anime_title': top_series_uhtml['anime'][0],
#                   'manga_link': top_series_uhtml['manga'][1],
#                   'manga_title': top_series_uhtml['manga'][0]}

#         mal_uhtml = user_info.mal_user(**kwargs)

#         await putter(f'{prefix}/adduhtml {username}-mal, {mal_uhtml}')
#     else:
#         await putter(f'{prefix} Could not find the MAL account {username}. ')
        
