import random

from constants.common import TrimmableClass
from constants.common import TYPED_NONES

# search
JIKAN_API = 'https://api.jikan.moe/v3'
JIKAN_SEARCH_API = 'https://api.jikan.moe/v3/search'

class Anime(TrimmableClass):
    FIELDS = {
        "mal_id": {
            "type": str
            },
        "url": {
            "type": str
            },
        "image_url": {
            "type": str
            },
        "name": {
            "type": str
            },
    }

class Manga(TrimmableClass):
    FIELDS = {
        "mal_id": {
            "type": str
            },
        "url": {
            "type": str
            },
        "image_url": {
            "type": str
            },
        "name": {
            "type": str
            },
    }

class AnimeStats(TrimmableClass):
    FIELDS = {
        "mean_score": {
            "type": float
            },
        "completed": {
            "type": int
            }, 
        "watching": {
            "type": int
            }, 
        "episodes_watched": {
            "type": int
            }
    }

class MangaStats(TrimmableClass):
    FIELDS = {
        "mean_score": {
            "type": float
            },  
        "completed": {
            "type": int
            }, 
        "reading": {
            "type": int
            }, 
        "chapters_read": {
            "type": int
            }
    }

class Favorites(TrimmableClass):
    FIELDS = {
        "manga": {
            "type": list
            }, 
        "anime": {
            "type": list
            }
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

    def unwrap(self, max_len=1):
        results = {
            'manga': [], 
            'anime': []
            }

        count = 0

        for manga, anime in zip(self.manga, self.anime):
            results['manga'].append(manga.unwrap())
            results['anime'].append(anime.unwrap())
            
            count += 1
            if max_len and count > max_len:
                break

        return results

class User(TrimmableClass):
    FIELDS = {
        "username": {
            "type": str,
            "readable_name": "_username"
            },
        "url": {
            "type": str,
            "readable_name": "_url"
            },
        "image_url": {
            "type": str,
            "readable_name": "_image_url"
            }, 
        "about": {
            "type": str,
            "readable_name": "About"
            }, 
        "anime_stats": {
            "type": dict,
            "readable_name": "Anime Stats"
            },
        "manga_stats": {
            "type": dict,
            "readable_name": "Manga Stats"
            },
        "favorites": {
            "type": dict,
            "readable_name": "Favorites"
            }
        }

    def __init__(self, kwargs):
        super().__init__(**kwargs)

        self.anime_stats = AnimeStats(**getattr(self, 'anime_stats', {}))
        self.manga_stats = MangaStats(**getattr(self, 'manga_stats', {}))
        self.favorites   = Favorites(**getattr(self, 'favorites', {}))

    def format_for_embed(self):
        embed = {
            "author": {
                "name": self.username,
                "url": self.url,
                "icon_url": self.image_url
            }
        }

        return embed