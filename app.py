import config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger
from models import db
from routes import api
from routes.auth import login_required, is_user_logged_in
import sanic
from sanic.response import html, text, json, redirect
import smtplib

app = sanic.Sanic(__name__)

app.static("/static", "static")
app.static("/favicon.ico", "static/favicon.ico")

app.blueprint(api)

env = Environment(
	loader=FileSystemLoader("templates"),
	autoescape=select_autoescape(["html"])
)
env.globals["url_for"] = app.url_for

app.env = env

# https://stackoverflow.com/a/51671065/11363384
db.bind(provider='postgres', user='', password='', host='localhost', database='postgres')
db.generate_mapping(create_tables=True)

@app.route("/")
@is_user_logged_in
async def landing_page(request, is_logged_in):
	if is_logged_in:
		return redirect(app.url_for("watchlist.root"))
	else:
		template = env.get_template("landing-page.html")
		return html(template.render())

@app.route("/account")
@login_required
async def account_page(request, user):
	template = env.get_template("account.html")
	return html(template.render(user=user))

@app.route("/signup")
async def register_page(request):
	failure = request.args.get("failure")
	message = None
	if failure:
		if failure == "name_missing":
			message = "First or last name missing."
		elif failure == "credential_missing":
			message = "Email or password missing."
		elif failure == "password_matching":
			message = "Passwords do not match."
		elif failure == "invalid_email":
			message = "The email address you entered is invalid."
		else:
			message = "Something went wrong"

	template = request.app.env.get_template("sign-up.html")
	return html(template.render())

@app.route("/signin")
async def login_page(request):
	failure = request.args.get("failure")
	message = None
	if failure:
		if failure == "password":
			message = "Incorrect email/password combination."
		else:
			message = "Something went wrong." 

	template = request.app.env.get_template("sign-in.html")
	return html(template.render())

if __name__ == "__main__":
	# ssl = {'cert': "localhost.pem", 'key': "localhost-key.pem"}
	app.run(host="0.0.0.0", port=8080, debug=True)