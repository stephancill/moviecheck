import os

SERVER_ENDPOINT = os.environ.get("SERVER_ENDPOINT", None)
POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME", None)
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
DB_NAME = os.environ.get("DB_NAME", None)
JWT_SECRET = os.environ.get("JWT_SECRET", None)
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", None)
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", EMAIL_ADDRESS)
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", None)
EMAIL_SMTP_SERVER = os.environ.get("EMAIL_SMTP_SERVER", None)
OMDB_API_KEY = os.environ.get("OMDB_API_KEY", None)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", None)