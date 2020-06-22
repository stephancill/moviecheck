import asyncio
import config
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from requests_cache import CachedSession
import scraper

class Movie:
    def __init__(self, title=None, year=None, imdb_id=None):
        self.title = title
        self.year = year
        self.imdb_id = imdb_id
        self.imdb_soup = None

    def get_imdb_soup(self):
        if not self.imdb_soup:
            self.imdb_soup = scraper.imdb_page_soup(imdb_id=self.imdb_id)
        return self.imdb_soup

    def populate_details(self):
        session = CachedSession(expires_after=60*60*24)
        if not self.imdb_id:
            result = scraper.imdb_search_year(self.title, self.year)
            if not result:
                return
            _, _, imdb_id = result
            self.imdb_id = imdb_id
        
        self.get_imdb_soup()
        
        # Order matters when manipulating soup (copies take too long)
        self.year = scraper.imdb_year(soup=self.imdb_soup)
        self.title = scraper.imdb_title(soup=self.imdb_soup)

    @staticmethod
    async def batch_populate_details(movies):
        with ThreadPoolExecutor(max_workers=20) as executor:
            loop = asyncio.get_event_loop()
            futures = [loop.run_in_executor(executor, movie.populate_details) for movie in movies]
            await asyncio.gather(*futures, return_exceptions=True)
        
class ResultMovie(Movie):
    def __init__(self, poster_url=None, rt_rating=None, rt_url=None, imdb_rating=None, in_watchlist=False, *args, **kwargs):
        self.poster_url = poster_url
        self.imdb_rating = imdb_rating
        self.rt_rating = rt_rating
        self.rt_url = rt_url
        self.in_watchlist = in_watchlist
        super().__init__(*args, **kwargs)

    def populate_details(self):
        self.get_imdb_soup()
        self.imdb_rating = scraper.imdb_rating(soup=self.imdb_soup)
        self.poster_url = scraper.imdb_poster_url(soup=self.imdb_soup)
        self.rt_rating = scraper.rt_rating(self.title, self.year)
        if self.rt_rating:
            self.rt_url = scraper.rt_url(self.title, self.year)
        super().populate_details()
        
class WatchlistMovie(Movie):
    def __init__(self, poster_url=None, in_watchlist=False, *args, **kwargs):
        self.poster_url = poster_url
        self.in_watchlist = in_watchlist
        super().__init__(*args, **kwargs)

    def populate_details(self):
        self.get_imdb_soup()
        self.poster_url = scraper.imdb_poster_url(soup=self.imdb_soup)
        super().populate_details()
    
class HistoryMovie(Movie):
    def __init__(self, genres=None, id=None, date=None, *args, **kwargs):
        self.genres = genres
        self.id = id
        self.date = date
        super().__init__(*args, **kwargs)

    def populate_details(self):
        self.get_imdb_soup()
        self.genres = scraper.imdb_genres(soup=self.imdb_soup)
        super().populate_details()