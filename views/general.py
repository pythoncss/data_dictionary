from flask_appbuilder import SimpleFormView, ModelView, expose
from app.forms.general import GetAdviceForm
from app import appbuilder, db
from flask import flash
from flask_mail import Mail, Message
from .utils import DataSQLAInterface
from app.models.general import FAQModel
from flask_babel import lazy_gettext as _
from flask_appbuilder.security.decorators import has_access
from flask_appbuilder.widgets import ListWidget


class GetAdviceView(SimpleFormView):
	route_base = "/get_advice"
	form = GetAdviceForm
	message = _("Thank you for filling up the form, we get back soon!")
	form_template = "/general/get_advice.html"


	@expose('/dataset', methods=['GET', 'POST'])
	def get_advice_on_dataset(self):
		form = GetAdviceForm()
		if form.validate_on_submit():
			form.data['dataset']
			form.data['message']
			flash(self.message, "info")
		return self.render_template(self.form_template, form=form)


class ListFAQWidget(ListWidget):
	template = "/widgets/faq_list.html"

class FAQView(ModelView):
	route_base = "/faq"
	datamodel = DataSQLAInterface(FAQModel)
	list_columns = ['faq_question', 'faq_text']
	label_columns = {'faq_question': 'FAQ Question', 'faq_text': 'FAQ Text'}

	list_template = "/general/faq.html"
	list_widget = ListFAQWidget


class FAQAdminView(ModelView):
	route_base = "/faq/admin"
	datamodel = DataSQLAInterface(FAQModel)
	list_columns = ['faq_question']
	label_columns = {'faq_question': 'FAQ Question', 'faq_text': 'FAQ Text'}



appbuilder.add_view_no_menu(GetAdviceView, "GetAdviceView")
appbuilder.add_view(FAQView, "FAQs", category="FAQs")
appbuilder.add_view(FAQAdminView, "FAQs Admin", category="FAQs")

