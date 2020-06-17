from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.user import User
from models.watchlist import Watchlist
from models.movie_item import MovieItem
from models.movie import Movie
from pony.orm import db_session, select
from sanic import Blueprint
from sanic import response

watchlist = Blueprint("watchlist", url_prefix="/watchlist")

@db_session
def is_in_default_watchlist(imdb_id, user):
	return Watchlist.select(
		lambda w: imdb_id in w.movie_items.imdb_id and 
		w.is_default and 
		w.user.id == user.id).first() != None
	
def default_watchlist(f):
	@wraps(f)
	def decorated_function(request, user, *args, **kwargs):
		with db_session(strict=False):
			watchlist = Watchlist.select(lambda w: w.user.id == user.id).first()
			if not watchlist:
				user = User.get(id=user.id)
				watchlist = Watchlist(user=user, is_default=True)
			watchlist.movie_items.load()
		return f(request, user, watchlist, *args, **kwargs)
	return decorated_function

@watchlist.route("/")
@login_required
@default_watchlist
async def root(request, user, watchlist):
	watchlist_movies = []
	for item in sorted(watchlist.movie_items, key=lambda x: x.date, reverse=True):
		movie = Movie.from_imdb_id(item.imdb_id)
		movie.in_watchlist = True
		watchlist_movies.append(movie)
	
	await Movie.batch_populate_details(watchlist_movies)

	history = []
	# For some reason watch_history does not preload properly
	with db_session():
		user = User.get(id=user.id)
		for item in sorted(user.watch_history, key=lambda x: x.date, reverse=True):
			movie = Movie.from_imdb_id(item.imdb_id)
			movie.populate_details()
			movie.date = item.date
			movie.id = item.id
			history.append(movie)

	template = request.app.env.get_template("watchlist.html")
	rendered = template.render(user=user, watchlist=watchlist_movies, history=history)
	return response.html(rendered)

@watchlist.route("/add/<movie_id>", methods=["POST"])
@login_required
@default_watchlist
async def add(request, user, watchlist, movie_id):
	logger.debug(movie_id)
	if not is_in_default_watchlist(movie_id, user):
		with db_session():
			watchlist = Watchlist.get(id=watchlist.id)
			item = MovieItem(imdb_id=movie_id, date=datetime.now(), watchlist=watchlist)
	return response.empty()

@watchlist.route("/seen/<movie_id>", methods=["POST"])
@login_required
@default_watchlist
async def seen(request, user, watchlist, movie_id):
	logger.debug(movie_id)
	with db_session():
		# TODO: Catche error if does not exist
		watchlist = Watchlist.get(id=watchlist.id)
		user = User.get(id=user.id)
		MovieItem.select(lambda m: m.imdb_id == movie_id and m.watchlist.id == watchlist.id).delete()
		movie = MovieItem(imdb_id=movie_id, date=datetime.now(), user=user)
	return response.empty()

@watchlist.route("/remove/<movie_id>", methods=["POST"])
@login_required
@default_watchlist
async def remove(request, user, watchlist, movie_id):
	logger.debug(movie_id)
	with db_session():
		watchlist = Watchlist.get(id=watchlist.id)
		MovieItem.select(lambda m: m.imdb_id == movie_id and m.watchlist.id == watchlist.id).delete()
	return response.empty()

@watchlist.route("/remove_history/<item_id>", methods=["POST"])
@login_required
async def remove_history(request, user, item_id):
	logger.debug(item_id)
	with db_session():
		MovieItem.select(lambda m: m.id == item_id).delete()
	return response.empty()

@watchlist.route("/edit_history/<item_id>", methods=["POST"])
@login_required
async def edit_history(request, user, item_id):
	logger.debug(item_id)
	logger.debug(request.form.get("date"))
	date_string = request.form.get("date")
	if date_string:
		with db_session():
			movie = MovieItem.select(lambda m: m.id == item_id).first()
			movie.date = datetime.strptime(date_string, "%Y-%m-%d")
	return response.empty()