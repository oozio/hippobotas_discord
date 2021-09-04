import random

from constants.common import User
from constants.common import TYPED_NONES

# search
JIKAN_API = 'https://api.jikan.moe/v3'
JIKAN_SEARCH_API = 'https://api.jikan.moe/v3/search'

class Anime(TrimmableClass):
    FIELDS = {
        "mal_id": int,
        "url": str,
        "image_url": str,
        "name": str
    }

class Manga(TrimmableClass):
    FIELDS = {
        "mal_id": int,
        "url": str,
        "image_url": str,
        "name": str
    }

class AnimeStats(TrimmableClass):
    FIELDS = {
        "mean_score": float, 
        "completed": int, 
        "watching": int, 
        "episodes_watched": int
    }

class MangaStats(TrimmableClass):
    FIELDS = {
        "mean_score": float, 
        "completed": int, 
        "reading": int, 
        "chapters_read": int
    }

class Favorites(TrimmableClass):
    FIELDS = {
        "manga": list,
        "anime": list
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.manga:
            self.manga = [Manga(**fav_manga) for fav_manga in self.manga]
        if self.anime:
            self.anime = [Anime(**fav_anime) for fav_anime in self.anime]            

    def random_manga(self):
        return random.choice(self.manga)

    def random_anime(self):
        return random.choice(self.anime)

    def raw(self, max_len=1):
        results = {
            'manga': [], 
            'anime': []
            }

        count = 0

        for manga, anime in zip(self.manga, self.anime):
            results['manga'].append(manga.raw())
            results['anime'].append(anime.raw())
            
            count += 1
            if max_len and count > max_len:
                break

        return results

class User(TrimmableClass):
    FIELDS = {
        "username": str, 
        "url": str,
        "image_url": str, 
        "about": str, 
        "anime_stats": dict, 
        "manga_stats": dict, 
        "favorites": dict
        }

    def __init__(self, kwargs):
        super().__init__(**kwargs)

        self.anime_stats = AnimeStats(**getattr(self, 'anime_stats', {}))
        self.manga_stats = MangaStats(**getattr(self, 'manga_stats', {}))
        self.favorites   = Favorites(**getattr(self, 'favorites', {}))