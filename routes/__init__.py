from .auth import auth
from sanic import Blueprint

api = Blueprint.group(auth)