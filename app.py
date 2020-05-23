import config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger
from models.user import User
from routes import api
from routes.auth import login_required
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

app.env = env

@app.route("/")
async def landing_page(request):
	template = env.get_template("landing-page.html")
	return html(template.render())

@app.route("/home")
@login_required
async def landing_page(request, user):
	template = env.get_template("index.html")
	return html(template.render(
		user=user,
		tag=request.args.get("tag")
	))

if __name__ == "__main__":
	# ssl = {'cert': "localhost.pem", 'key': "localhost-key.pem"}
	app.run(host="0.0.0.0", port=8080, debug=True)