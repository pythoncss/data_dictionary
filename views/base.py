from flask_appbuilder import BaseView
from flask_appbuilder import PublicFormView, expose
from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.forms.auth import ForgotPasswordForm
from app import appbuilder
from flask import flash, url_for, current_app, redirect, request, g, session
from app import db
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_appbuilder.security.forms import ResetPasswordForm



def get_token(user, expiration=100):
	s = Serializer(current_app.config['SECRET_KEY'], expiration)
	return s.dumps({'user': user.id}).decode('utf-8')


def verify_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return None
    id = data.get('user')
    if id:
        return db.session.query(User).get(id)
    return None



class ForgotPasswordView(PublicFormView):
	route_base = "/forgot_password"
	form = ForgotPasswordForm
	form_title = "Recover Password"
	message = "A link will be sent to the Email Address, if it exists."

	def form_post(self, form):
		if form.validate_on_submit():
			try:
				user = db.session.query(User).filter_by(email=form.email.data).first_or_404()
			except:
				flash("Invalid Email Address", "error")

			if user:
				self.send_email(user)
				flash(self.message, "info")

	def send_email(self, user):
		mail = Mail(self.appbuilder.get_app)
		msg = Message()
		msg.subject = "Password reset link"
		url = url_for('ResetPasswordFormView.this_form_get', _external=True, reset_hash=get_token(user))
		msg.html = "Hello {}. <br> Please click below the link to reset your password <br>{}".format(user.first_name, url)
		msg.recipients = [user.email]
		print(url)
		###mail.send(msg)


class ResetPasswordFormView(PublicFormView):
	form = ResetPasswordForm
	route_base = "/reset"
	form_title = "Reset Password"
	message = "Please login"

	def form_post(self, form):
		user = verify_token(request.args.get('reset_hash'))
		if user:
			self.appbuilder.sm.reset_password(user.id, form.password.data)
			flash(self.message, "info")
		else:
			flash("Invalid token", "error")



appbuilder.add_view_no_menu(ForgotPasswordView, "ForgotPasswordView")
appbuilder.add_view_no_menu(ResetPasswordFormView, "ResetPasswordFormView")




