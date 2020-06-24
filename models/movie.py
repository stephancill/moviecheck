import asyncio
import config
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from loguru import logger
from requests_cache import CachedSession
import scraper

def requires_omdb_json(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.omdb_json:
            session = CachedSession(expires_after=60*60*24*7)
            if self.imdb_id:
                r = session.get("http://www.omdbapi.com/", params={
                    "apiKey": config.OMDB_API_KEY,
                    "i": self.imdb_id
                })
                self.omdb_json = r.json()
            else:
                r = session.get("http://www.omdbapi.com/", params={
                    "apiKey": config.OMDB_API_KEY,
                    "t": self.title,
                    "y": self.year
                })
                self.omdb_json = r.json()
        return f(self, self.omdb_json, *args, **kwargs)
    return wrapper

class Movie:
    def __init__(self, title=None, year=None, imdb_id=None, type=None, omdb_json=None):
        self.title = title
        self.year = year
        self.imdb_id = imdb_id
        self.type = type
        self.omdb_json = omdb_json

    @requires_omdb_json
    def populate_details(self, json):     
        self.year = json.get("Year")
        self.title = json.get("Title")
        self.imdb_id = json.get("imdbID")
        self.type = json.get("Type")

    @staticmethod
    async def batch_populate_details(movies):
        with ThreadPoolExecutor(max_workers=20) as executor:
            loop = asyncio.get_event_loop()
            futures = [loop.run_in_executor(executor, movie.populate_details) for movie in movies]
            await asyncio.gather(*futures, return_exceptions=True)
        
class ResultMovie(Movie):
    def __init__(self, poster_url=None, rt_rating=None, rt_url=None, imdb_rating=None, imdb_url=None, in_watchlist=False, *args, **kwargs):
        self.poster_url = poster_url
        self.imdb_rating = imdb_rating
        self.imdb_url = imdb_url
        self.rt_rating = rt_rating
        self.rt_url = rt_url
        self.in_watchlist = in_watchlist
        super().__init__(*args, **kwargs)

    @requires_omdb_json
    def populate_details(self, json):
        super().populate_details()
        self.poster_url = json.get("Poster")
        self.imdb_rating = json.get("imdbRating")
        if json.get("imdbID"):
            self.imdb_url = "https://www.imdb.com/title/" + json.get("imdbID")
        self.rt_rating = scraper.rt_rating(self.title, self.year)
        if self.rt_rating:
            self.rt_url = scraper.rt_url(self.title, self.year)
        
        
class WatchlistMovie(Movie):
    def __init__(self, poster_url=None, in_watchlist=False, *args, **kwargs):
        self.poster_url = poster_url
        self.in_watchlist = in_watchlist
        super().__init__(*args, **kwargs)

    @requires_omdb_json
    def populate_details(self, json):
        super().populate_details()
        self.poster_url = json.get("Poster")
    
class HistoryMovie(Movie):
    def __init__(self, genres=None, id=None, date=None, rating=None, *args, **kwargs):
        self.genres = genres
        self.id = id
        self.date = date
        self.rating = rating
        super().__init__(*args, **kwargs)

    @requires_omdb_json
    def populate_details(self, json):
        super().populate_details()
        self.genres = json.get("Genre", "").split(", ")

class ImportResultMovie(WatchlistMovie):
    def __init__(self, date=None, *args, **kwargs):
        self.date = date
        super().__init__(*args, **kwargs)