class Movie:
    def __init__(self, title, year, imdb_id, poster_url, type, rt_rating=None, imdb_rating=None):
        self.title = title
        self.year = year
        self.imdb_id = imdb_id
        self.poster_url = poster_url
        self.type = type
        self.rt_rating = rt_rating
        self.imdb_rating = imdb_rating
