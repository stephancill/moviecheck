from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.user import User
from sanic import Blueprint
from sanic import response

watchlist = Blueprint("watchlist", url_prefix="/watchlist")

@watchlist.route("/")
@login_required
async def root(request, user):
	logger.debug(user)
	template = request.app.env.get_template("watchlist.html")
	return response.html(template.render(user=user))

@watchlist.route("/add/<movie_id>", methods=["POST"])
@login_required
async def add(request, user, movie_id):
	logger.debug(movie_id)
	return response.empty()

@watchlist.route("/seen/<movie_id>", methods=["POST"])
@login_required
async def seen(request, user, movie_id):
	logger.debug(movie_id)
	return response.empty()
