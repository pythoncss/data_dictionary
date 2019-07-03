from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Boolean


class DataUser(User):
	__tablename__ = 'ab_user'
	new_user = Column(Boolean, default=True)
