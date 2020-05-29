import config
from loguru import logger
from requests_cache import CachedSession

class Movie:
    def __init__(self, title=None, poster_url=None, year=None, imdb_id=None, genres=[], rt_rating=None, imdb_rating=None):
        self.title = title
        self.year = year
        self.imdb_id = imdb_id
        self.poster_url = poster_url
        self.genres = genres
        self.rt_rating = rt_rating
        self.imdb_rating = imdb_rating
    
    @staticmethod
    def from_omdb(json):
        omdb_keymap = {
            "Title": "title",
            "Year": "year",
            "imdbID": "imdb_id",
            "Poster": "poster_url"
        }
        return Movie(**{omdb_keymap[key]: value for key, value in json.items() if key in omdb_keymap})

    @staticmethod
    def from_tmdb(json):
        tmdb_base = "https://image.tmdb.org/t/p/w185"
        movie = Movie()
        movie.title = json["title"]
        movie.year = json["release_date"].split("-")[0]
        movie.poster_url = tmdb_base + json["poster_path"]
        return movie

    @staticmethod
    def from_imdb_id(imdb_id):
        session = CachedSession(expires_after=60*60*24)
        r = session.get("http://www.omdbapi.com/", params={
            "apiKey": config.OMDB_API_KEY,
            "i": imdb_id
        })
        json = r.json()
        movie = Movie.from_omdb(json)
        movie.populate_details()
        return movie

    # TODO: Async implementation
    def populate_details(self):
        session = CachedSession(expires_after=60*60*24)
        if self.imdb_id:
            r = session.get("http://www.omdbapi.com/", params={
                "apiKey": config.OMDB_API_KEY,
                "i": self.imdb_id
            })
            json = r.json()
        else:
            r = session.get("http://www.omdbapi.com/", params={
                "apiKey": config.OMDB_API_KEY,
                "t": self.title,
                "y": self.year
            })
            json = r.json()
            self.imdb_id = json.get("imdbID")
            if not self.imdb_id:
                logger.debug("Could not find movie with title '{}' ({})".format(self.title, self.year))
                return

        self.imdb_rating = json.get("imdbRating")
        rt_rating = ([x for x in json.get("Ratings", []) if x["Source"] == "Rotten Tomatoes"] or [{}])[0].get("Value")
        if rt_rating:
            self.rt_rating = rt_rating.split("/")[0]

        self.genres = json.get("Genre", "").split(", ")
        
