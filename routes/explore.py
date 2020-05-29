from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.movie import Movie
from models.user import User
import requests
from requests_cache import CachedSession
from sanic import Blueprint
from sanic import response

explore = Blueprint("explore", url_prefix="/explore")

def get_trending():
	r = requests.get("https://api.themoviedb.org/3/discover/movie", {
		"api_key": config.TMDB_API_KEY,
		"sort_by": "popularity.desc"
	})
	movies_json = []
	for movie_json in r.json().get("results", [])[:5]:
		movie = Movie.from_tmdb(movie_json)
		movie.populate_details()
		movies_json.append(movie.__dict__)
	
	return movies_json


@explore.route("/")
@login_required
async def root(request, user):
	template = request.app.env.get_template("explore.html")
	trending_json = get_trending()
	return response.html(template.render(user=user, trending=trending_json))

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
	results_json = []
	for movie_json in r.json().get("Search", []):
		movie = Movie.from_omdb(movie_json)
		movie.populate_details()
		results_json.append(movie.__dict__)

	template = request.app.env.get_template("explore.html")
	return response.html(template.render(user=user, results=results_json, query=query))
