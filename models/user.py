import bcrypt
from datetime import datetime
from loguru import logger
from pony.orm import *

db = Database()

class User(db.Entity):
	id = PrimaryKey(int, auto=True)
	email = Optional(str)
	password_hash = Optional(str)
	first_name = Optional(str)
	last_name = Optional(str)
	is_verified = Optional(bool)
	date_registered = Optional(datetime)
	active_token = Optional(str)
	watch_history = Set('MovieItem', cascade_delete=True)
	watchlists = Set('Watchlist', cascade_delete=True)

	@staticmethod
	def hash_password(password: str):
		password = password.encode("utf-8")
		return bcrypt.hashpw(password, bcrypt.gensalt()).decode()

	def check_password(self, password):
		password = password.encode("utf-8")
		password_hash = self.password_hash.encode("utf-8")
		return bcrypt.checkpw(password, password_hash)
