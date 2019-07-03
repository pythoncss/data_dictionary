from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, ForeignKey, SmallInteger, Date, Boolean
from sqlalchemy.orm import relationship
from citext import CIText
from flask import Markup
from flask_appbuilder.models.mixins import AuditMixin


class FAQModel(Model):
	faq_id = Column(Integer, primary_key=True)
	faq_question = Column(String(255))
	faq_text = Column(Text)

	def __repr__(self):
		return self.faq_question

