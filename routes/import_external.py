from .auth import login_required
import csv
from datetime import datetime, timedelta
from loguru import logger
from models.movie import ImportResultMovie
from sanic import Blueprint
from sanic import response
from .watchlist import history_id

import_external = Blueprint("import_external", url_prefix="/import")

def process_csv(file_body):
	titles = {}
	reader = csv.reader(file_body, dialect="excel")
	headers = next(reader)
	for row in reader:
		full_title, date = row
		year, month, day = [int(x) for x in date.split("/")]
		date = datetime(year=year, month=month, day=day)
		main_title = full_title.split(":")[0]
		if not main_title in titles:
			titles[main_title] = date
		elif titles[main_title] < date:
			titles[main_title] = date
		
	movies = []
	for title, date in titles.items():
		movie = ImportResultMovie(title=title, date=date)
		movies.append(movie)

	return movies

@import_external.route("/", methods=["POST"])
@login_required
async def process_upload(request, user):
	# TODO: Handle error when cannot parse file
	template = request.app.env.get_template("import.html")
	file_body = request.files['netflix-data'][0].body.decode().strip().split("\n")
	imported_items = process_csv(file_body)
	
	await ImportResultMovie.batch_populate_details(imported_items)
	
	not_imported = []
	for movie in imported_items:
		if not history_id(movie.imdb_id, movie.date, user):
			not_imported.append(movie)

	return response.html(template.render(user=user, results=[x for x in not_imported if x.imdb_id]))

@import_external.route("/")
@login_required
async def root(request, user):
	template = request.app.env.get_template("import.html")
	return response.html(template.render(user=user))