from functools import wraps
from jinja2 import Environment, FileSystemLoader, select_autoescape

def requires_app(f):
    @wraps(f)
    def wrapper(app, *args, **kwargs):
        template = app.env.get_template("generic-response.html")
        return f(app, template, *args, **kwargs)
    return wrapper

class GenericResponse:

    @staticmethod
    @requires_app
    def forgot_password_email_success(app, template, debug_link=None):
        if debug_link:
            link = debug_link
            link_caption = "Reset your password"
        else:
            link = app.url_for("landing_page")
            link_caption = "Back"
        return template.render(
            title="Success",
            heading="Password reset link sent.",
            subheading="We've sent you a password reset link. Check your inbox.",
            link=link,
            link_caption=link_caption
        )

    @staticmethod
    @requires_app
    def token_expired(app, template):
        return template.render(
			title="Error",
			heading="Token expired",
			subheading="Please try again.",
			link=app.url_for("landing_page"),
			link_caption="Back"
		)

    @staticmethod
    @requires_app
    def token_invalid(app, template):
        return template.render(
			title="Error",
			heading="Invalid token",
			subheading="Please try again.",
			link=app.url_for("landing_page"),
			link_caption="Back"
		)

    @staticmethod
    @requires_app
    def password_reset_success(app, template):
        return template.render(
            title="Success",
            heading="Password successfully reset.",
            subheading="You may now use your new password to sign in.",
            link=app.url_for("login_page"),
            link_caption="Sign in"
        )

    @staticmethod
    @requires_app
    def verification_email_success(app, template, debug_link=None):
        if app.debug:
            link = debug_link
            link_caption = "Verify"
        else:
            link = app.url_for("landing_page")
            link_caption = "Back"

        return template.render(
            title="Success",
            heading="Email verification required.",
            subheading="We've sent you a verification email. Check your inbox.",
            link=link,
            link_caption=link_caption
        )

    @staticmethod
    @requires_app
    def email_verify_success(app, template):
        return template.render(
            title="Success",
            heading="Email verified.",
            subheading="Your email has been verified, you may now sign in.",
            link=app.url_for("login_page"),
            link_caption="Sign in"
        )

    @staticmethod
    @requires_app
    def account_deleted_success(app, template):
        return template.render(
            title="Success",
            heading="Account Deleted.",
            subheading="Your account has been deleted successfully.",
            link=app.url_for("landing_page"),
            link_caption="Back"
        ) 
    