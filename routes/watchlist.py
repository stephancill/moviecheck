from .auth import login_required
import config
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from models.user import User
from sanic import Blueprint
from sanic.response import redirect, text, html, empty

watchlist = Blueprint("watchlist", url_prefix="/watchlist")

@watchlist.route("/")
@login_required
async def root(request, user):
	logger.debug(user)
	template = request.app.env.get_template("watchlist.html")
	return html(template.render(user=user))
