from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.movie import Movie, ResultMovie
import requests
from requests_cache import CachedSession
from sanic import Blueprint
from sanic import response
from scraper import rt_trending, imdb_trending, imdb_search
from .watchlist import default_watchlist, is_in_default_watchlist

explore = Blueprint("explore", url_prefix="/explore")

async def get_trending(count=5):
	titles = imdb_trending()
	movies = []
	for title, year, imdb_id in titles[:count]:
		movie = ResultMovie()
		movie.title = title
		movie.year = year
		movie.imdb_id = imdb_id
		movies.append(movie)
	
	await ResultMovie.batch_populate_details(movies)

	return movies

@explore.route("/")
@login_required
async def root(request, user):
	# TODO: Centralize this initialization (in_watchlist, populate_details)
	template = request.app.env.get_template("explore.html")
	trending = await get_trending(5)
	await ResultMovie.batch_populate_details(trending)
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
		"s": query
	})
	json = r.json()
	movies = []
	for movie_json in r.json().get("Search", []):
		if not movie_json.get("Type") in ["series", "movie"] or movie_json.get("Poster") == "N/A":
			continue
		movie = ResultMovie(imdb_id=movie_json.get("imdbID"))
		movie.in_watchlist = is_in_default_watchlist(movie.imdb_id, user)
		movies.append(movie)
	
	await Movie.batch_populate_details(movies)

	template = request.app.env.get_template("explore.html")
	return response.html(template.render(user=user, results=movies, query=query))
