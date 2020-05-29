import os
import loguru

try:
	SERVER_ENDPOINT = os.environ["SERVER_ENDPOINT"]
	MONGO_HOST = os.environ["MONGO_HOST"]
	MONGO_PORT = os.environ["MONGO_PORT"]
	MONGO_URI = os.environ["MONGO_URI"]
	DB_NAME = os.environ["DB_NAME"]
	JWT_SECRET = os.environ["JWT_SECRET"]
	EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
	EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
	EMAIL_SMTP_SERVER = os.environ["EMAIL_SMTP_SERVER"]
	OMDB_API_KEY = os.environ["OMDB_API_KEY"]
	TMDB_API_KEY = os.environ["TMDB_API_KEY"]
except Exception as e:
	loguru.exception(e)