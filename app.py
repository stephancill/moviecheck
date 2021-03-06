import config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger
from models import db
from routes import api
from routes.auth import login_required, is_user_logged_in, failure_message
from routes.explore import get_trending
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
env.globals["app"] = app
env.globals["config"] = config

app.env = env

# https://stackoverflow.com/a/51671065/11363384
db.bind(provider='postgres', user=config.POSTGRES_USERNAME, password=config.POSTGRES_PASSWORD, host=config.POSTGRES_HOST, database=config.DB_NAME)
db.generate_mapping(create_tables=True)

@app.route("/")
@is_user_logged_in
async def landing_page(request, is_logged_in):
	if is_logged_in:
		return redirect(app.url_for("watchlist.root"))
	else:
		trending = await get_trending(4)
		template = env.get_template("landing-page.html")
		return html(template.render(trending=trending))

@app.route("/account")
@login_required
async def account_page(request, user):
	template = env.get_template("account.html")
	return html(template.render(user=user))

@app.route("/signup")
@failure_message
async def register_page(request, message):
	template = request.app.env.get_template("sign-up.html")
	return html(template.render(failure=message))

@app.route("/signin")
@failure_message
async def login_page(request, message):
	template = request.app.env.get_template("sign-in.html")
	return html(template.render(failure=message))

@app.route("/forgot")
async def forgot_password_page(request):
	template = request.app.env.get_template("forgot-password.html")
	return html(template.render())

@app.route("/privacy")
async def privacy_policy_page(request):
	template = request.app.env.get_template("privacy-policy.html")
	return html(template.render())

@app.route("/tos")
async def tos_page(request):
	template = request.app.env.get_template("terms-of-service.html")
	return html(template.render())

if __name__ == "__main__":
	# ssl = {'cert': "localhost.pem", 'key': "localhost-key.pem"}
	app.run(host="0.0.0.0", port=8080, debug=True)