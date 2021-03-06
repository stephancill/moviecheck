import config
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from .generic_responses import GenericResponse
from itsdangerous import TimedJSONWebSignatureSerializer, URLSafeTimedSerializer, SignatureExpired
from loguru import logger
from models.user import User
from pony.orm import db_session, commit
from premailer import transform
from sanic import Blueprint
from sanic.response import redirect, text, html, empty
import smtplib
from smtplib import SMTPRecipientsRefused

auth = Blueprint("auth", url_prefix="/auth")

serializer = TimedJSONWebSignatureSerializer(config.JWT_SECRET)
url_safe_serializer = URLSafeTimedSerializer(config.JWT_SECRET)

def login_required(f):
	@wraps(f)
	def decorated_function(request, *args, **kwargs):
		try:
			serialized_token = request.cookies.get("token")
			if not serialized_token: raise Exception("No token, sign in")
			user_id = serializer.loads(str.encode(serialized_token)).get("user_id")
			with db_session():
				user = User.get(id=user_id)
				user.load()
			if not user: raise Exception("Could not find user.")
		except Exception as e:
			logger.info(e)
			return redirect(request.app.url_for('login_page'))
		return f(request, user, *args, **kwargs)
	return decorated_function

def is_user_logged_in(f):
	@wraps(f)
	def decorated_function(request, *args, **kwargs):
		try:
			serialized_token = request.cookies.get("token")
			if not serialized_token: raise Exception("No token, sign in")
			user_id = serializer.loads(str.encode(serialized_token)).get("user_id")
			with db_session():
				user = User.get(id=user_id)
		except Exception as e:
			logger.info(e)
			return f(request, False, *args, **kwargs)
		return f(request, True, *args, **kwargs)
	return decorated_function


def failure_message(f):
	@wraps(f)
	def decorated_function(request, *args, **kwargs):
		failure = request.args.get("failure")
		message = None
		if failure:
			# Register
			if failure == "name_missing":
				message = "First or last name missing."
			elif failure == "credential_missing":
				message = "Email or password missing."
			elif failure == "password_matching":
				message = "Passwords do not match."
			elif failure == "invalid_email":
				message = "The email address you entered is invalid."
			elif failure == "exists":
				message = "A user with that email already exists."
			elif failure == "unauthorized":
				message = "Unauthorized."
			# Login
			elif failure == "password":
				message = "Incorrect email/password combination."
			# Forgot 
			elif failure == "invalid_email":
				message = "Could not send email."
			else:
				message = "Something went wrong"
		return f(request, *args, message, **kwargs)
	return decorated_function

@auth.route("/forgot", methods=["POST"])
async def forgot_password(request):
	email = request.form.get("email")
	if not email: 
		logger.info("Bad request, no email field")
		return empty(status=400)
	
	response_html = GenericResponse.forgot_password_email_success(request.app)
	
	with db_session():
		user = User.get(email=email)
	if not user:
		logger.info("Could not find user. Returning response")
		return html(response_html)

	reset_token = url_safe_serializer.dumps(str(user.id))
	relative_url = request.app.url_for("auth.reset_password", token=reset_token)
	full_url = "{host}{location}".format(host=config.SERVER_ENDPOINT, location=relative_url)

	with db_session():
		User[user.id].active_token = reset_token

	if request.app.debug:
		response_html = GenericResponse.forgot_password_email_success(request.app, debug_link=full_url)

	response = html(response_html)

	subject = "MovieCheck - Reset your password"
	template = request.app.env.get_template("emails/forgot_password.html")
	rendered = template.render(cta_url=full_url)
	email_html = transform(rendered)
	text = "Reset your password: {}".format(full_url)

	success = request.app.debug or send_email(user.email, subject, email_html, text)
	if not success:
		logger.critical("Could not send email")
		return redirect(request.app.url_for("auth.forgot_password_page")+"?failure=invalid_email")
	else:
		return response
	
@auth.route("/reset_password/<token>", methods=["GET"])
async def reset_password_page(request, token):
	global url_safe_serializer
	try:
		user_id = url_safe_serializer.loads(token, max_age=60*60*24)
		with db_session():
			user = User.get(id=user_id, active_token=token)
		if not user: raise Exception()
	except SignatureExpired as e:
		return html(GenericResponse.token_expired(request.app))
	except Exception as e:
		return html(GenericResponse.token_invalid(request.app))

	template = request.app.env.get_template("change-password.html")
	return html(template.render(token=token))

@auth.route("/reset_password/<token>", methods=["POST"])
async def reset_password(request, token):
	global url_safe_serializer
	try:
		user_id = url_safe_serializer.loads(token, max_age=60*60*24)
		with db_session():
			user = User.get(id=user_id, active_token=token)
		if not user: raise Exception()
	except SignatureExpired as e:
		return html(GenericResponse.token_expired(request.app))
	except Exception as e:
		return html(GenericResponse.token_invalid(request.app))

	try:
		password = request.form.get("password")
		confirm_password = request.form.get("confirm_password")
		if not confirm_password or not password: raise Exception("credential_missing")
		if password != confirm_password: raise Exception("password_matching")
	except Exception as e:
		logger.info(e)
		return redirect(request.app.url_for("reset_password_page")+"?failure={}".format(e))

	password_hash = User.hash_password(password)
	with db_session():
		User[user_id].set(password_hash=password_hash, active_token="")

	response_html = GenericResponse.password_reset_success(request.app)
	return html(response_html)

@auth.route("/register", methods=["POST"])
async def register(request):
	try:
		first_name = request.form.get("first_name").strip()
		last_name = request.form.get("last_name").strip()
		email = request.form.get("email").strip()
		password = request.form.get("password")
		confirm_password = request.form.get("confirm_password")
		if not first_name or not last_name: raise Exception("name_missing")
		if not email or not password: raise Exception("credential_missing")
		if password != confirm_password: raise Exception("password_matching")
	except Exception as e:
		logger.info(e)
		return redirect(request.app.url_for("register_page")+"?failure={}".format(e))
	
	with db_session():
		if User.exists(email=email):
			logger.info("User with email {} exists.".format(email))
			return redirect(request.app.url_for("register_page")+"?failure=exists")
	
		password_hash = User.hash_password(password)
		user = User(
			email=email, 
			password_hash=password_hash, 
			first_name=first_name, 
			last_name=last_name,
			date_registered=datetime.now()
		)

	with db_session():
		user = User.get(email=email)
		temp_token = url_safe_serializer.dumps(str(user.id))
	return redirect(request.app.url_for("auth.send_verification_email", token=temp_token))

@auth.route("/send_verification/<token>")
def send_verification_email(request, token):
	global url_safe_serializer
	try:
		user_id = url_safe_serializer.loads(token, max_age=10)
	except Exception as e:
		response_html = GenericResponse.token_invalid(request.app)
		return html(response_html)
	
	verification_token = url_safe_serializer.dumps(user_id)
	with db_session():
		user = User.get(id=user_id)
	if not user:
		return html("<p>Something went wrong...</p><a href='/'>")

	verification_url = "{host}{location}".format(
		host=config.SERVER_ENDPOINT, 
		location=request.app.url_for("auth.verify_email", token=verification_token)
	)

	subject = "MovieCheck - Verify your email"
	template = request.app.env.get_template("emails/confirm_email.html")
	rendered = template.render(cta_url=verification_url)
	email_html = transform(rendered)
	text = "Verify your email: {}".format(verification_url)

	success = request.app.debug or send_email(user.email, subject, email_html, text)
	if not success:
		user.delete()
		return redirect(request.app.url_for("register_page")+"?failure=invalid_email")

	return html(GenericResponse.verification_email_success(request.app, debug_link=verification_url))
	

@auth.route("/verify/<token>")
async def verify_email(request, token):
	global url_safe_serializer
	token_issue = None
	try:
		user_id = url_safe_serializer.loads(token, max_age=60*60*24)
	except SignatureExpired as e:
		user_id = url_safe_serializer.loads(token)
		with db_session():
			User.get(id=user_id).delete()
		return html(GenericResponse.token_expired(request.app))
	except Exception as e:
		return html(GenericResponse.token_invalid(request.app))
	
	with db_session():
		User[user_id].set(is_verified=True)

	return html(GenericResponse.email_verify_success(request.app))
	

@auth.route("/login", methods=["POST"])
async def login(request):
	email = request.form.get("email")
	password = request.form.get("password")
	if not email or not password:
		logger.info("Missing fields")
		return redirect(request.app.url_for("login_page")+"?failure=invalid")

	with db_session():
		user = User.get(email=email)

	if not (user and user.check_password(password)):
		logger.info("User not found/incorrect password ({})".format(email))
		return redirect(request.app.url_for("login_page")+"?failure=password")
	
	if not user.is_verified:
		temp_token = url_safe_serializer.dumps(str(user.id))
		return redirect(request.app.url_for("auth.send_verification_email", token=temp_token))

	response = redirect(request.app.url_for("landing_page"))
	serializer = TimedJSONWebSignatureSerializer(config.JWT_SECRET, expires_in=60*60*24*7)
	access_token = serializer.dumps({"user_id": str(user.id)})
	response.cookies["token"] = access_token.decode()
	response.cookies["token"]["expires"] = datetime.now() + timedelta(days=1)

	return response

@auth.route("/logout")
async def logout(request):
	response = redirect(request.app.url_for("landing_page"))
	del response.cookies["token"]
	return response

@auth.route("/delete_account", methods=["POST"])
@login_required
async def delete_account(request, user):
	with db_session():
		user = User.get(id=user.id).delete()

	return html(GenericResponse.account_deleted_success(request.app))


def send_email(recipient, subject, html, text):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = config.EMAIL_ADDRESS
	msg['To'] = recipient
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')
	msg.attach(part1)
	msg.attach(part2)
	
	s = smtplib.SMTP(config.EMAIL_SMTP_SERVER)
	s.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
	try:
		s.send_message(msg)
	except SMTPRecipientsRefused as e:
		logger.critical(e)
		return False
	finally:
		s.quit()
	
	return True