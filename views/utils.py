import sqlalchemy as sa
from flask_appbuilder.models.sqla.interface import SQLAInterface
from citext import CIText
from flask import g


class DataSQLAInterface(SQLAInterface):
	def is_string(self, col_name):
		try:
			return (isinstance(self.list_columns[col_name].type, sa.types.String) or 
				isinstance(self.list_columns[col_name].type, CIText))
		except:
			return False

	def is_text(self, col_name):
		try:
			return isinstance(self.list_columns[col_name].type, sa.types.Text)
		except:
			return False


def is_dataset_approved(approved):

	if 'Reader' in [role.name for role in g.user.roles] and approved is True:
		return True
	elif 'Reader' not in [role.name for role in g.user.roles]:
		return True
	return False

def format_date(obj):
	if obj is not None:
		return obj.strftime('%Y-%m-%d')
	return

def dataset_has_owner(obj):
	if obj is not None:
		return obj.data_source_owner
	return