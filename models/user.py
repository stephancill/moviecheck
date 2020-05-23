import bcrypt
from loguru import logger
from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField
import requests

class User(Document):
	email = StringField(required=True)
	password_hash = StringField(required=True)
	first_name = StringField(required=True)
	last_name = StringField(required=True)
	is_verified = BooleanField(default=False)
	date_registered = DateTimeField(required=True)
	active_token = StringField()

	@staticmethod
	def exists(email):
		return User.objects(email=email).first() != None

	@staticmethod
	def hash_password(password: str):
		password = password.encode("utf-8")
		return bcrypt.hashpw(password, bcrypt.gensalt())

	def check_password(self, password):
		password = password.encode("utf-8")
		password_hash = self.password_hash.encode("utf-8")
		return bcrypt.checkpw(password, password_hash)
