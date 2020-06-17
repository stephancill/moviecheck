from bs4 import BeautifulSoup
from copy import copy
from requests_cache import CachedSession
from functools import wraps

def rt_search_wrapper(f):
    @wraps(f)
    def wrapper(title, year, *args, **kwargs):
        session = CachedSession(expire_after=60*60*24)
        # https://www.rottentomatoes.com/napi/search/?query=parasite&offset=0&limit=10
        stripped_title = "".join([x for x in title if x.isalnum() or x == " "]).lower().strip()
        response = session.get("https://www.rottentomatoes.com/napi/search", params={
            "query": stripped_title,
            "offset": 0,
            "limit": 10
        })
        json = response.json()
        return f(stripped_title, year, json, *args, **kwargs)
    return wrapper

def imdb_wrapper(f):
    @wraps(f)
    def wrapper(page_html=None, imdb_id=None, soup=None, *args, **kwargs):
        if not (page_html or imdb_id or soup):
            return None
        if imdb_id:
            session = CachedSession(expire_after=60*60*24)
            r = session.get("https://www.imdb.com/title/{}".format(imdb_id))
            page_html = r.text
        soup = soup or BeautifulSoup(page_html, "html.parser")
        return f(soup, *args, **kwargs)
    return wrapper

def imdb_page_soup(imdb_id):
    session = CachedSession(expire_after=60*60*24)
    r = session.get("https://www.imdb.com/title/{}".format(imdb_id))
    page_html = r.text
    return BeautifulSoup(page_html, "html.parser")

def rt_trending():
    session = CachedSession(expire_after=60*60*24)
    page = session.get("https://www.rottentomatoes.com").text
    soup = BeautifulSoup(page, "html.parser")
    return [(x.get_text(), None) for x in soup.select(".dynamic-text-list__item-title")]

def imdb_trending():
    session = CachedSession(expire_after=60*60*24)
    page = session.get("https://www.imdb.com/chart/moviemeter").text
    soup = BeautifulSoup(page, "html.parser")
    results = []
    for result in soup.select("td.titleColumn"):
        title = result.select("a")[0].get_text()
        imdb_id = result.a.get("href").split("/")
        try:
            imdb_id = result.a.get("href").split("/title/")[1].split("/")[0]
        except IndexError:
            imdb_id = None
            continue
        try:
            year = result.select(".secondaryInfo")[0].get_text().strip("(").strip(")")
            int(year)
        except:
            year = None
            continue
        
        results.append((title, year, imdb_id))
    return results

@imdb_wrapper
def imdb_title(soup):
    # TODO: Localized title when available
    elements = soup.select(".title_wrapper h1")
    title = None
    for element in elements:
        element.span.decompose()
        title = element.get_text().strip()
        if title:
            break

    return title

@imdb_wrapper
def imdb_year(soup):
    years = [x.get_text() for x in soup.select("#titleYear a")]
    if len(years) > 0:
        return years[0].strip()
    else:
        return None

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

def imdb_search(query):
    session = CachedSession(expire_after=60*60*24)
    stripped_query = "".join([x for x in query if x.isalnum() or x == " "]).lower()
    r = session.get("https://www.imdb.com/find", params={
        "q": stripped_query,
        "s": "tt",
        "ttype": "ft"
    })
    page_html = r.text
    soup = BeautifulSoup(page_html, "html.parser")
    results = []
    for result in soup.select(".result_text"):
        title = result.a.get_text()
        imdb_id = result.a.get("href").split("/")
        try:
            imdb_id = result.a.get("href").split("/title/")[1].split("/")[0]
        except IndexError:
            imdb_id = None
            continue
        result.a.decompose()
        try:
            year = result.get_text().split("(")[1].split(")")[0]
            int(year)
        except:
            year = None
            continue
        
        results.append((title, year, imdb_id))
    
    return results


def imdb_search_year(title, year):
    results = imdb_search("{} {}".format(title, year))
    if len(results > 0):
        return results[0]
    else:
        return None

@rt_search_wrapper
def rt_rating(stripped_title, year, json):
    for movie in json.get("movies", []):
        if str(movie.get("year")) == str(year):
            title_stripped = "".join([x for x in movie.get("name") if x.isalnum() or x == " "]).lower().strip()
            if stripped_title in title_stripped or title_stripped in stripped_title:
                rating = movie.get("meterScore")
                if rating:
                    return "{}%".format(rating)
                return None
    return None

@rt_search_wrapper
def rt_url(stripped_title, year, json):
    for movie in json.get("movies", []):
        if str(movie.get("year")) == str(year):
            title_stripped = "".join([x for x in movie.get("name") if x.isalnum() or x == " "]).lower().strip()
            if stripped_title in title_stripped or title_stripped in stripped_title:
                url = movie.get("url")
                if url:
                    return "https://www.rottentomatoes.com{}".format(url)
                return None
    return None

if __name__ == "__main__":
    print(rt_rating("wolf of wall street", "2013"))
    print(rt_url("wolf of wall street", "2013"))
    # print(imdb_title(imdb_id="tt10886166"))
    # print(imdb_year(imdb_id="tt10886166"))
    # print(imdb_rating(imdb_id="tt10886166"))
