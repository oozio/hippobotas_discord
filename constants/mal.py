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

    def prettify(self):
        return f"[{self.name}]({self.url})"

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

    def prettify(self):
        return f"[{self.name}]({self.url})"



class AnimeStats(TrimmableClass):
    FIELDS = {
        "mean_score": {
            "type": float,
            "readable_name": "Mean Score"
            },
        "completed": {
            "type": int,
            "readable_name": "# Completed"
            }, 
        "watching": {
            "type": int,
            "readable_name": "# Watching"
            }, 
        "episodes_watched": {
            "type": int,
            "readable_name": "Episodes watched"
            }
    }
    
        

class MangaStats(TrimmableClass):
    FIELDS = {
        "mean_score": {
            "type": float,
            "readable_name": "Mean Score"
            },  
        "completed": {
            "type": int,
            "readable_name": "# Completed"
            }, 
        "reading": {
            "type": int,
            "readable_name": "# Reading"
            }, 
        "chapters_read": {
            "type": int,
            "readable_name": "Chapters Read"
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
        return random.choice(self.manga) if self.manga else None

    def random_anime(self):
        return random.choice(self.anime) if self.anime else None

    def unwrap(self, raw=False):
        results = {
            'manga': [], 
            'anime': []
            }

        for manga, anime in zip(self.manga, self.anime):
            results['manga'].append(manga.unwrap())
            results['anime'].append(anime.unwrap())

        return results

    def prettify(self, content_type=None):
        pretty_str = ""

        if not content_type:
            raise ValueError('favorites.prettify() received no content type')

        if content_type == 'manga': 
            chosen_content = self.random_manga()
        elif content_type == 'anime':
            chosen_content = self.random_anime()
        else:
            raise ValueError('favorites.prettify() received unknown content type')
        
        if chosen_content:
            pretty_str += f"Random favorite: {chosen_content.prettify()}\n"
        else:
            pretty_str += f"Random favorite: no favorites!\n"

        return pretty_str
        
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
        rand_fav_anime = self.favorites.prettify('anime')
        rand_fav_manga = self.favorites.prettify('manga')
        
        embed = {
            "author": {
                "name": self.username,
                "url": self.url,
                "icon_url": self.image_url
            },
            "fields": [
                {
                    "name": "Anime Stats",
                    "value": f"{self.anime_stats.prettify()}\n{rand_fav_anime}",
                    "inline": True
                },
                {
                    "name": "Manga Stats",
                    "value": f"{self.manga_stats.prettify()}\n{rand_fav_manga}",
                    "inline": True
                }
            ]
        }

        return embed