from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.movie import Movie
from models.user import User
import requests
from sanic import Blueprint
from sanic import response

explore = Blueprint("explore", url_prefix="/explore")

@explore.route("/")
@login_required
async def root(request, user):
	template = request.app.env.get_template("explore.html")
	return response.html(template.render(user=user))

@explore.route("/search")
@login_required
async def search(request, user):
    # TODO: Ratings
    query = request.args.get("query", default="")
    r = requests.get("http://www.omdbapi.com/", {
        "apiKey": config.OMDB_API_KEY,
        "s": query,
        "type": "movie"
    })
    json = r.json()
    omdb_keymap = {
        "Title": "title",
        "Year": "year",
        "imdbID": "imdb_id",
        "Poster": "poster_url",
        "Type": "type"
    }
    movies_json = []
    for movie_json in r.json().get("Search", []):
        movie = Movie(**{omdb_keymap[key]: value for key, value in movie_json.items()})
        movies_json.append(movie.__dict__)

    template = request.app.env.get_template("explore.html")
    return response.html(template.render(user=user, results=movies_json))
