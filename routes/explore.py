from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.movie import Movie
import requests
from requests_cache import CachedSession
from sanic import Blueprint
from sanic import response
from scraper import rt_trending, imdb_trending
from .watchlist import default_watchlist, is_in_default_watchlist

explore = Blueprint("explore", url_prefix="/explore")

# async def populate_details(movies):
# 	with ThreadPoolExecutor(max_workers=20) as executor:
# 		loop = asyncio.get_event_loop()
# 		futures = [loop.run_in_executor(executor, movie.populate_details) for movie in movies]
# 		await asyncio.gather(*futures, return_exceptions=True) 

def get_trending():
	# session = CachedSession(expires_after=60*60*24)
	# r = session.get("https://api.themoviedb.org/3/discover/movie", params={
	# 	"api_key": config.TMDB_API_KEY,
	# 	"sort_by": "popularity.desc"
	# })
	# movies = []
	# for movie_json in r.json().get("results", [])[:7]:
	# 	movie = Movie.from_tmdb(movie_json)
	# 	movies.append(movie)
	titles = imdb_trending()
	movies = []
	for title, year in titles:
		movie = Movie()
		movie.title = "".join([x for x in title if x.isalnum() or x == " "])
		movie.year = year
		movies.append(movie)
	
	return movies


@explore.route("/")
@login_required
async def root(request, user):
	# TODO: Centralize this initialization (in_watchlist, populate_details)
	template = request.app.env.get_template("explore.html")
	trending = get_trending()
	await Movie.batch_populate_details(trending)
	for movie in trending:
		movie.in_watchlist = is_in_default_watchlist(movie.imdb_id, user)
	return response.html(template.render(user=user, trending=[x for x in trending if x.imdb_id]))

@explore.route("/search")
@login_required
async def search(request, user):
	query = request.args.get("query", default="").strip()
	session = CachedSession(expires_after=60*60*24)
	r = session.get("http://www.omdbapi.com/", params={
		"apiKey": config.OMDB_API_KEY,
		"s": query,
		"type": "movie"
	})
	json = r.json()
	movies = []
	for movie_json in r.json().get("Search", []):
		movie = Movie.from_omdb(movie_json)
		movie.in_watchlist = is_in_default_watchlist(movie.imdb_id, user)
		movies.append(movie)
	
	await Movie.batch_populate_details(movies)

	template = request.app.env.get_template("explore.html")
	return response.html(template.render(user=user, results=movies, query=query))
