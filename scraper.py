from bs4 import BeautifulSoup
from requests_cache import CachedSession

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

if __name__ == "__main__":
    print(imdb_trending())