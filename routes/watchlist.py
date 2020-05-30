from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.user import User
from models.watchlist import Watchlist
from models.movie_item import MovieItem
from models.movie import Movie
from sanic import Blueprint
from sanic import response

watchlist = Blueprint("watchlist", url_prefix="/watchlist")

def default_watchlist(f):
	@wraps(f)
	def decorated_function(request, user, *args, **kwargs):
		watchlist = Watchlist.objects(user_id=user.id, is_default=True).first()
		if not watchlist:
			watchlist = Watchlist(user_id=user.id, is_default=True)
			watchlist.save() 
		return f(request, user, watchlist, *args, **kwargs)
	return decorated_function

@watchlist.route("/")
@login_required
@default_watchlist
async def root(request, user, watchlist):
	logger.debug(user)
	watchlist_movies = []
	for item in watchlist.items:
		movie = Movie.from_imdb_id(item.imdb_id)
		watchlist_movies.append(movie)

	history = []
	for item in sorted(user.watch_history, key=lambda x: x.date, reverse=True):
		movie = Movie.from_imdb_id(item.imdb_id)
		movie.date = item.date
		history.append(movie)

	template = request.app.env.get_template("watchlist.html")
	return response.html(template.render(user=user, watchlist=watchlist_movies, history=history))

@watchlist.route("/add/<movie_id>", methods=["POST"])
@login_required
@default_watchlist
async def add(request, user, watchlist, movie_id):
	logger.debug(movie_id)
	item = MovieItem(imdb_id=movie_id, date=datetime.now())
	# TODO: Investigate add_to_set not working
	Watchlist.objects(id=watchlist.id).update(add_to_set__items=item)
	return response.empty()

@watchlist.route("/seen/<movie_id>", methods=["POST"])
@login_required
@default_watchlist
async def seen(request, user, watchlist, movie_id):
	logger.debug(movie_id)
	Watchlist.objects(id=watchlist.id).update(pull__items__imdb_id=movie_id)
	item = MovieItem(imdb_id=movie_id, date=datetime.now())
	User.objects(id=user.id).update(push__watch_history=item)
	return response.empty()

@watchlist.route("/remove/<movie_id>", methods=["POST"])
@login_required
@default_watchlist
async def remove(request, user, watchlist, movie_id):
	logger.debug(movie_id)
	Watchlist.objects(id=watchlist.id).update(pull__items__imdb_id=movie_id)
	return response.empty()
