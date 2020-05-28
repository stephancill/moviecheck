import os

try:
	SERVER_ENDPOINT = os.environ["SERVER_ENDPOINT"]
except Exception:
	SERVER_ENDPOINT = "https://localhost:8080"

try:
	MONGO_HOST = os.environ["MONGO_ENDPOINT"]
except Exception:
	MONGO_HOST = "localhost"

try:
	MONGO_PORT = os.environ["MONGO_PORT"]
except Exception:
	MONGO_PORT = 27017

try:
	MONGO_URI = os.environ["MONGO_URI"]
except Exception:
	DB_NAME = "moviecheck"

try:
	DB_NAME = os.environ["DB_NAME"]
except Exception:
	DB_NAME = None

try:
	JWT_SECRET = os.environ["JWT_SECRET"]
except Exception:
	JWT_SECRET = "SOMETHING SECRET"

try:
	EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
except Exception:
	EMAIL_ADDRESS = "SERVCIE EMAIL"

try:
	EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
except Exception:
	EMAIL_PASSWORD = "SERVICE EMAIL PASSWORD"

try:
	EMAIL_SMTP_SERVER = os.environ["EMAIL_SMTP_SERVER"]
except Exception:
	EMAIL_SMTP_SERVER = "SERVICE MAIL SMTP SERVER"

try:
	OMDB_API_KEY = os.environ["OMDB_API_KEY"]
except Exception:
	OMDB_API_KEY = "OMDB_API_KEY"

try:
	TMDB_API_KEY = os.environ["TMDB_API_KEY"]
except Exception:
	TMDB_API_KEY = "TMDB_API_KEY"