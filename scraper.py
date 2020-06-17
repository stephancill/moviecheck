from bs4 import BeautifulSoup
from requests_cache import CachedSession
from functools import wraps

def imdb_wrapper(f):
    @wraps(f)
    def wrapper(page_html=None, imdb_id=None, *args, **kwargs):
        if not (page_html or imdb_id):
            return None
        if imdb_id:
            session = CachedSession(expire_after=60*60*24)
            page_html = session.get("https://www.imdb.com/title/{}".format(imdb_id)).text
        soup = BeautifulSoup(page_html, "html.parser")
        return f(soup, *args, **kwargs)
    return wrapper

def rt_trending():
    session = CachedSession(expire_after=60*60*24)
    page = session.get("https://www.rottentomatoes.com").text
    soup = BeautifulSoup(page, "html.parser")
    return [(x.get_text(), None) for x in soup.select(".dynamic-text-list__item-title")]

def imdb_trending():
    session = CachedSession(expire_after=60*60*24)
    page = session.get("https://www.imdb.com/chart/moviemeter").text
    soup = BeautifulSoup(page, "html.parser")
    return [(x.select("a")[0].get_text(), x.select(".secondaryInfo")[0].get_text().strip("(").strip(")")) for x in soup.select("td.titleColumn")]

@imdb_wrapper
def imdb_rating(soup):
    rating = [x.get_text() for x in soup.select(".ratingValue strong span")]
    if len(rating) > 0:
        return rating[0]
    else:
        return None

@imdb_wrapper   
def imdb_poster_url(soup):
    poster_urls = [x.get("src", None) for x in soup.select(".poster a img")]
    if len(poster_urls) > 0:
        return poster_urls[0]
    else:
        return None

@imdb_wrapper   
def imdb_genres(soup):
    genres = [x.get_text() for x in soup.select(".subtext a")][:-1]
    return genres

def rt_rating(title, year):
    
    session = CachedSession(expire_after=60*60*24)
    # https://www.rottentomatoes.com/napi/search/?query=parasite&offset=0&limit=10
    stripped_title = "".join([x for x in title if x.isalnum() or x == " "]).lower()
    response = session.get("https://www.rottentomatoes.com/napi/search", params={
        "query": stripped_title,
        "offset": 0,
        "limit": 10
    })
    json = response.json()
    for movie in json.get("movies", []):
        if movie.get("year") == year:
            title_stripped = "".join([x for x in movie.get("name") if x.isalnum() or x == " "]).lower()
            if stripped_title in title_stripped:
                return movie.get("meterScore")
    
    return None

if __name__ == "__main__":
    print(rt_rating("wolf of wall street", 2013))