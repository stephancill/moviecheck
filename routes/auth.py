import config
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from itsdangerous import TimedJSONWebSignatureSerializer, URLSafeTimedSerializer, SignatureExpired
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger
from models.user import User
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
			user = User.objects(id=user_id).first()
			if not user: raise Exception("User not found")
		except Exception as e:
			logger.info(e)
			return redirect(request.app.url_for('auth.login_page'))

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

@auth.route("/forgot", methods=["GET"])
@failure_message
async def forgot_password_page(request, message):
	template = request.app.request.app.env.get_template("template.html")
	return html(template.render(
		pageName="forgot.html", 
		pageScript="/assets/js/min/auth.min.js",
		alert_message=message))

@auth.route("/forgot", methods=["POST"])
async def forgot_password(request):
	email = request.form.get("email")
	if not email: 
		logger.info("Bad request, no email field")
		return empty(status=400)
	
	response_html = "<p>We've sent you a password reset link. Check your inbox.</p>"
	
	user = User.objects(email=email).first()
	if not user:
		logger.info("Could not find user. Returning response")
		return html(response_html)

	reset_token = url_safe_serializer.dumps(str(user.id))
	relative_url = request.app.url_for("auth.reset_password", token=reset_token)
	full_url = "{host}{location}".format(host=config.SERVER_ENDPOINT, location=relative_url)

	User.objects(id=user.id).update_one(active_token=reset_token)

	if request.app.debug:
		response_html = response_html + "<a href='{url}'>Reset your password</a>".format(url=full_url)

	response = html(response_html)

	subject = "Turn Left Media Analytics - Reset your password"
	email_html = """\
		<html>
			<head></head>
			<body>
				<p>A password reset link was requested for this account.</p>
				<a href="{}">Reset your password</a>
			</body>
		</html>
	""".format(full_url)
	text = "Reset your password: {}".format(full_url)

	success = send_email(user.email, subject, email_html, text)
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
		user = User.objects(id=user_id, active_token=token).first()
		if not user: raise Exception()
	except SignatureExpired as e:
		return html("<p>Token expired</p><a href='/'>Back</a>")
	except Exception as e:
		return html("<p>Invalid token</p><a href='/'>Back</a>")
	
	template = request.app.request.app.env.get_template("template.html")
	return html(template.render(
		pageName="change-password.html", 
		pageScript=""))

@auth.route("/reset_password/<token>", methods=["POST"])
async def reset_password(request, token):
	global url_safe_serializer
	try:
		user_id = url_safe_serializer.loads(token, max_age=60*60*24)
		user = User.objects(id=user_id, active_token=token).first()
		if not user: raise Exception()
	except SignatureExpired as e:
		return html("<p>Token expired</p><a href='/'>Back</a>")
	except Exception as e:
		return html("<p>Invalid token</p><a href='/'>Back</a>")

	try:
		password = request.form.get("password")
		confirm_password = request.form.get("confirm_password")
		if not confirm_password or not password: raise Exception("credential_missing")
		if password != confirm_password: raise Exception("password_matching")
	except Exception as e:
		logger.info(e)
		return redirect(request.app.url_for("reset_password_page")+"?failure={}".format(e))

	password_hash = User.hash_password(password).decode()
	User.objects(id=user_id).update_one(password_hash=password_hash, active_token=None)
	return html("<p>Password successfully reset</p><a href='/login'>Login</a>")


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

	if User.exists(email):
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
	user.save()
	
	temp_token = url_safe_serializer.dumps(str(user.id))
	return redirect(request.app.url_for("auth.send_verification_email", token=temp_token))

@auth.route("/send_verification/<token>")
def send_verification_email(request, token):
	global url_safe_serializer
	try:
		user_id = url_safe_serializer.loads(token, max_age=10)
	except Exception as e:
		return html("<p>Invalid token</p><a href='/'>")
		pass
	
	verification_token = url_safe_serializer.dumps(user_id)

	user = User.objects(id=user_id).first()
	if not user:
		return html("<p>Something went wrong...</p><a href='/'>")

	verification_url = "{host}{location}".format(
		host=config.SERVER_ENDPOINT, 
		location=request.app.url_for("auth.verify_email", token=verification_token)
	)

	subject = "Turn Left Media Analytics - Verify your email"
	email_html = """\
		<html>
			<head></head>
			<body>
				<p>Thank you for registering on Turn Left Media Analytics by Neon Solutions.</p>
				<a href="{}">Verify email</a>
			</body>
		</html>
	""".format(verification_url)
	text = "Verify your email: {}".format(verification_url)

	success = send_email(user.email, subject, email_html, text)
	if not success:
		user.delete()
		return redirect(request.app.url_for("register_page")+"?failure=invalid_email")

	if request.app.debug:
		return html("<p>We've sent you a verification email. Check your inbox.</p><a href='/auth/verify/{}'>Verify</a>".format(verification_token))
	else:
		return html("<p>We've sent you a verification email. Check your inbox.</p>")
	

@auth.route("/verify/<token>")
async def verify_email(request, token):
	global url_safe_serializer
	try:
		user_id = url_safe_serializer.loads(token, max_age=60*60*24)
	except SignatureExpired as e:
		user_id = url_safe_serializer.loads(token)
		User.objects(id=user_id).delete()
		return html("<p>Token expired</p><a href='/register'>Register</a>")
	except Exception as e:
		return html("<p>Invalid token</p><a href='/register'>Register</a>")

	User.objects(id=user_id).update_one(is_verified=True)

	return html("<p>Email verified</p><a href='/login'>Login</a>")
	

@auth.route("/login", methods=["POST"])
async def login(request):
	email = request.form.get("email")
	password = request.form.get("password")
	if not email or not password:
		logger.info("Missing fields")
		return redirect(request.app.url_for("login_page")+"?failure=invalid")

	user = User.objects(email=email).first()

	if not (user and user.check_password(password)):
		logger.info("User not found/incorrect password ({})".format(email))
		return redirect(request.app.url_for("login_page")+"?failure=password")
	
	if not user.is_verified:
		temp_token = url_safe_serializer.dumps(str(user.id))
		return redirect(request.app.url_for("auth.send_verification_email", token=temp_token))

	response = redirect(request.app.url_for("root"))
	serializer = TimedJSONWebSignatureSerializer(config.JWT_SECRET, expires_in=60*60*24)
	access_token = serializer.dumps({"user_id": str(user.id)})
	response.cookies["token"] = access_token.decode()
	response.cookies["token"]["expires"] = datetime.now() + timedelta(days=1)

	return response

@auth.route("/logout")
async def logout(request):
	response = redirect(request.app.url_for("root"))
	del response.cookies["token"]
	return response

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
	s.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
	try:
		s.send_message(msg)
	except SMTPRecipientsRefused as e:
		logger.critical(e)
		return False
	finally:
		s.quit()
	
	return True