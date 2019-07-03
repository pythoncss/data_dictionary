from flask_appbuilder import BaseView, expose, ModelView, MultipleView
from app import appbuilder, db
from .utils import DataSQLAInterface, is_dataset_approved, format_date, dataset_has_owner
from app.models.datas import DataSet, Tag, DataSourceOwner, TagValue, DatasetView, DataSetFavorite, DatasetAttribute, DataSetAttachment
from flask import request, jsonify, abort, g, send_file
from collections import defaultdict
from flask_appbuilder.security.decorators import has_access
from flask_appbuilder.models.sqla.filters import FilterStartsWith
from flask_appbuilder.widgets import ListWidget
from .datas import DataSetAttributeView, DataSourceOwner, TagView, TagValueView
from datetime import datetime
from app.utils.download_dataset import download_excel


def dataset_attributes(dataset_id):
	rows = db.session.query(DatasetAttribute).filter(DatasetAttribute.dataset_id==dataset_id).all()
	return [{
	'column_name': attr.column_name, 
	'attribute_description': attr.attribute_description, 
	'datatype': attr.data_type and attr.data_type.datatype_name or ''} for attr in rows]

def dataset_attachments(dataset_id):
	rows = db.session.query(DataSetAttachment).filter(DataSetAttachment.dataset_id==dataset_id).all()
	return [{
	'file': row.dataset_attachment_file
	} for row in rows]

class DataSetListWidget(ListWidget):
	template = 'widgets/list_dataset.html'

class DataSetAttachmentView(ModelView):
	list_title = "Attachments"
	datamodel = DataSQLAInterface(DataSetAttachment)
	list_columns = show_columns = ['dataset_attachment_name', 'dataset_attachment_file', 'download']


class DataSetView(ModelView):
	route_base = "/data_set"
	datamodel = DataSQLAInterface(DataSet)
	list_widget = DataSetListWidget
	extra_args = {'tags': db.session.query(Tag)}
	list_title = "Datasets"

	label_columns = {
        'data_source'                        : 'Data Source',
        'dataset_description_'               : 'Description',
        'dataset_name_'                      : 'Name',
        'dataset_schema'                     : 'Schema',
        'history_held_since'                 : 'History Held Since',
        'refresh_frequency'                  : 'Refresh Frequency',
        'storage_location'                   : 'Storage Location',
        'personally_identifiable_information': 'Personally Identifiable',
        'data_source_owner_'                 : 'Data Owner'
    }


	list_columns = ['dataset_name_' ,'dataset_short_description', 'data_source_owner_']
	edit_columns = add_columns = ['dataset_name', 'dataset_short_description', 'dataset_description', 'dataset_schema', 
	'storage_location', 'data_source', 'history_held_since', 'refresh_frequency', 'recency_at_time_of_refresh', 
	'personally_identifiable_information', 'data_source_owner', 'tags', 'tags_value', 'approved',
	'primary_key', 'data_supplier', 'projects_using_this']
	show_columns = ['dataset_name_' ,'dataset_schema' ,'storage_location' , 'history_held_since' ,
    'refresh_frequency', 'data_source', 'dataset_description_', 'data_source_owner_']

	related_views = [DataSetAttributeView, DataSourceOwner, DataSetAttachmentView]

	add_template = "/datas/add_with_tinymce.html"
	edit_template = "/datas/edit_with_tinymce.html"

	add_title = "Add new Data set"

	@expose('/list/')
	@has_access
	def list(self):
		widgets = self._list()
		return self.render_template(self.list_template,
                                    title=self.list_title,
                                    widgets=widgets)

	@expose('/show/<pk>', methods=['GET'])
	@has_access
	def show(self, pk):
		pk = self._deserialize_pk_if_composite(pk)

		dataset_count = db.session.query(DatasetView).filter(DatasetView.dataset_id==pk).first()
		if dataset_count:
			dataset_count.data_set_count += 1
			db.session.add(dataset_count)
		else:
			db.session.add(DatasetView(dataset_id=pk, data_set_count=1))
		db.session.commit()
		return super().show(pk)

	@expose('/get_dataset_view_count/<dataset_id>')
	@has_access
	def get_dataset_view_count(self, dataset_id):
		count=get_dataset_view_count(dataset_id)
		return jsonify(count)

	@expose('/get_dataset_fab_count/<dataset_id>/<user_id>', methods=['GET', 'POST'])
	@has_access
	def get_dataset_fab_count(self, dataset_id, user_id):
		if request.method == 'POST':
			dataset_fab = db.session.query(DataSetFavorite).filter(DataSetFavorite.dataset_id==dataset_id, 
				DataSetFavorite.user_id==user_id).first()
			if dataset_fab:
				dataset_fab.dataset_fab_count += 1
				db.session.add(dataset_fab)
			else:
				db.session.add(DataSetFavorite(dataset_id=dataset_id, user_id=user_id, dataset_fab_count=1))
			db.session.commit()

		try:
			count = db.session.query(DataSetFavorite).filter(DataSetFavorite.dataset_id==dataset_id, 
				DataSetFavorite.user_id==user_id).one()
		except:
			count = 0

		if count:
			return jsonify(count.dataset_fab_count)
		else:
			return jsonify(0)


	@expose('/list_new')
	@has_access
	def list_new(self):
		today = datetime.today().strftime('%Y-%m-%d')
		datasets = db.session.query(DataSet).order_by(DataSet.created_on.desc()).all()
		tags = db.session.query(Tag).all()

		output= [{'dataset_name': result.dataset_name,\
			 'dataset_description': result.dataset_description, 'tags': [tag.tag_name for tag in result.tags], 
			 'dataset_id': result.dataset_id, 'is_admin': True if 'Admin' in [role.name for role in g.user.roles] else False, 
			 'is_new': True if today == result.created_on.strftime('%Y-%m-%d') else False,
			 'tags_value': [tv.tag_value_name for tv in result.tags_value], 
			 'data_source': result.data_source and result.data_source.data_source_name or '', 'created_by': result.created_by.username,
			 'created_on': result.created_on, 'dataset_schema': result.dataset_schema, 
			 'storage_location': result.storage_location, 'row_count': result.row_count, 
			 'primary_key': result.primary_key, 'data_supplier': result.data_supplier, 
			 'data_source_owner': dataset_has_owner(result.data_source_owner), 
			 'history_held_since': result.history_held_since, 'changed_by': result.changed_by, 
			 'changed_on': result.changed_on, 'position': result.position, 
			 'projects_using_this': result.projects_using_this, 
			 'tags_list': [{'tag_name': tag.tag_name, 'tag_values': [elem.tag_value_name if elem in result.tags_value else None  for elem in tag.tag_value]} for tag in result.tags],
			 'columns': dataset_attributes(result.dataset_id), 'attachments': dataset_attachments(result.dataset_id) }
			 for result in datasets if is_dataset_approved(result.approved)]

		return self.render_template("/dataset/list_new.html", datasets=output, tags=tags)

	@expose('/list_all')
	@has_access
	def list_all(self):
		today = datetime.today().strftime('%Y-%m-%d')
		datasets = db.session.query(DataSet).order_by(DataSet.created_on.desc()).all()
		output= [{'dataset_name': result.dataset_name,\
			 'dataset_description': result.dataset_description, 'tags': [tag.tag_name for tag in result.tags],
			 'dataset_id': result.dataset_id, 'is_admin': True if 'Admin' in [role.name for role in g.user.roles] else False, 
			 'is_new': True if today == result.created_on.strftime('%Y-%m-%d') else False,
			 'tags_value': [tv.tag_value_name for tv in result.tags_value], 
			 'data_source': result.data_source and result.data_source.data_source_name or '', 'created_by': result.created_by.username,
			 'created_on': format_date(result.created_on), 'dataset_schema': result.dataset_schema, 
			 'storage_location': result.storage_location and result.storage_location.storage_location_name or '', 'row_count': result.row_count,
			 'primary_key': result.primary_key, 'data_supplier': result.data_supplier, 
			 'data_source_owner': dataset_has_owner(result.data_source_owner), 
			 'history_held_since': format_date(result.history_held_since), 'changed_by': result.changed_by.username, 
			 'changed_on': format_date(result.changed_on), 'position': result.position, 
			 'projects_using_this': result.projects_using_this, 
			 'tags_list': [{'tag_name': tag.tag_name, 'tag_values': [elem.tag_value_name if elem in result.tags_value else None  for elem in tag.tag_value]} for tag in result.tags], 
			 'columns': dataset_attributes(result.dataset_id), 'attachments': dataset_attachments(result.dataset_id) }
			 for result in datasets if is_dataset_approved(result.approved) ]
		return jsonify(output)

	@expose('/search')
	@has_access
	def search(self):
		today = datetime.today().strftime('%Y-%m-%d')

		filter_by_tag_value = request.args.get('_flt_0_tags_value', None)
		if filter_by_tag_value:
			tag_values_list = [int(f) for f in filter_by_tag_value.split(",")]
			results = db.session.query(DataSet).join((TagValue, DataSet.tags_value)).\
			filter(TagValue.tag_value_id.in_(tag_values_list)).all()
			output= [{'dataset_name': result.dataset_name,\
			 'dataset_description': result.dataset_description, 'tags': [tag.tag_name for tag in result.tags], 
			 'dataset_id': result.dataset_id, 'is_admin': True if 'Admin' in [role.name for role in g.user.roles] else False, 
			 'is_new': True if today == result.created_on.strftime('%Y-%m-%d') else False,
			 'tags_value': [tv.tag_value_name for tv in result.tags_value], 
			 'data_source': result.data_source and result.data_source.data_source_name or '', 'created_by': result.created_by.username,
			 'created_on': format_date(result.created_on), 'dataset_schema': result.dataset_schema, 
			 'storage_location': result.storage_location and result.storage_location.storage_location_name or '', 'row_count': result.row_count,
			 'primary_key': result.primary_key, 'data_supplier': result.data_supplier, 
			 'data_source_owner': dataset_has_owner(result.data_source_owner), 
			 'history_held_since': format_date(result.history_held_since), 'changed_by': result.changed_by.username, 
			 'changed_on': format_date(result.changed_on), 'position': result.position, 
			 'projects_using_this': result.projects_using_this, 
			 'tags_list': [{'tag_name': tag.tag_name, 'tag_values': [elem.tag_value_name if elem in result.tags_value else None  for elem in tag.tag_value]} for tag in result.tags], 
			 'columns': dataset_attributes(result.dataset_id), 'attachments': dataset_attachments(result.dataset_id) }
			 for result in results if is_dataset_approved(result.approved)]
			return jsonify(output)

		filter_by_dataset_name = request.args.get('_flt_0_dataset_name', None, type=str)
		if filter_by_dataset_name:
			results = db.session.query(DataSet).filter(DataSet.dataset_description.match(filter_by_dataset_name))

			output= [{'dataset_name': result.dataset_name,\
			 'dataset_description': result.dataset_description, 'tags': [tag.tag_name for tag in result.tags], 
			 'dataset_id': result.dataset_id, 'is_admin': True if 'Admin' in [role.name for role in g.user.roles] else False, 
			 'is_new': True if today == result.created_on.strftime('%Y-%m-%d') else False,
			 'tags_value': [tv.tag_value_name for tv in result.tags_value], 
			 'data_source': result.data_source and result.data_source.data_source_name or '', 'created_by': result.created_by.username,
			 'created_on': format_date(result.created_on), 'dataset_schema': result.dataset_schema, 
			 'storage_location': result.storage_location.storage_location_name, 'row_count': result.row_count, 
			 'primary_key': result.primary_key, 'data_supplier': result.data_supplier, 
			 'data_source_owner': dataset_has_owner(result.data_source_owner), 
			 'history_held_since': format_date(result.history_held_since), 'changed_by': result.changed_by.username, 
			 'changed_on': format_date(result.changed_on), 'position': result.position, 
			 'projects_using_this': result.projects_using_this, 
			 'tags_list': [{'tag_name': tag.tag_name, 'tag_values': [elem.tag_value_name if elem in result.tags_value else None  for elem in tag.tag_value]} for tag in result.tags], 
			 'columns': dataset_attributes(result.dataset_id), 'attachments': dataset_attachments(result.dataset_id) } if not is_dataset_approved(result.approved) else {}
			 for result in results]
			return jsonify(output)

	@expose('/atoz_search')
	@has_access
	def atoz_search(self):
		today = datetime.today().strftime('%Y-%m-%d')
		filter_by_dataset_name = request.args.get('_flt_0_dataset_name', None, type=str)
		if filter_by_dataset_name:
			results = db.session.query(DataSet).filter(DataSet.dataset_name.startswith(filter_by_dataset_name)).all()
			output= [{'dataset_name': result.dataset_name,\
			 'dataset_description': result.dataset_description, 'tags': [tag.tag_name for tag in result.tags], 
			 'dataset_id': result.dataset_id, 'is_admin': True if 'Admin' in [role.name for role in g.user.roles] else False, 
			 'is_new': True if today == result.created_on.strftime('%Y-%m-%d') else False,
			 'tags_value': [tv.tag_value_name for tv in result.tags_value], 
			 'data_source': result.data_source and result.data_source.data_source_name or '', 'created_by': result.created_by.username,
			 'created_on': format_date(result.created_on), 'dataset_schema': result.dataset_schema, 
			 'storage_location': result.storage_location.storage_location_name, 'row_count': result.row_count, 
			 'primary_key': result.primary_key, 'data_supplier': result.data_supplier, 
			 'data_source_owner': dataset_has_owner(result.data_source_owner), 
			 'history_held_since': format_date(result.history_held_since), 'changed_by': result.changed_by.username, 
			 'changed_on': format_date(result.changed_on), 'position': result.position, 
			 'projects_using_this': result.projects_using_this, 
			 'tags_list': [{'tag_name': tag.tag_name, 'tag_values': [elem.tag_value_name if elem in result.tags_value else None  for elem in tag.tag_value]} for tag in result.tags], 
			 'columns': dataset_attributes(result.dataset_id), 'attachments': dataset_attachments(result.dataset_id)} if not is_dataset_approved(result.approved) else {}
			 for result in results]
			return jsonify(output)
		return abort(404)


	@expose('/download')
	@has_access
	def download(self):
		dataset_ids = request.args.get('datasets')
		if dataset_ids:
			dataset_ids = dataset_ids.split(',')

		if not dataset_ids:
			abort(404)

		datasetattrs = db.session.query(DatasetAttribute).filter(DatasetAttribute.dataset_id.in_(dataset_ids)).all()
		results  = db.session.query(DataSet).filter(DataSet.dataset_id.in_(dataset_ids)).all()
		datasets = [{
		'dataset_name'		 : result.dataset_name, 
		'dataset_description': result.dataset_description,
		'tags'				 : [tag.tag_name for tag in result.tags],
		'tags_value'		 : [tv.tag_value_name for tv in result.tags_value],
		'dataset_schema'	 : result.dataset_schema,
		'storage_location'	 : result.storage_location.storage_location_name,
		'metas'				 : {'primary_key': result.primary_key, 
								'data_supplier': result.data_supplier, 
								'row_count': result.row_count,
								'data_source_owner': dataset_has_owner(result.data_source_owner),
								'history_held_since': result.history_held_since,
								'created_on': result.created_on,
								'created_by': result.created_by.username,
								'changed_on': result.changed_on
								},
		'data_set_attributes': [{'column_name': attr.column_name, 
								 'attribute_description': attr.attribute_description, 
								 'datatype': attr.data_type.datatype_name,
								 'count_of_unique_values': attr.count_of_unique_values,
								 'count_of_null_values': attr.count_of_null_values} for attr in datasetattrs
							   ]
		} for result in results]
		#return str(datasets)
		path = download_excel(datasets, 'data_set')
		return send_file(path, as_attachment=True)


appbuilder.add_view(DataSetView, "Data Sets", category="Data", href='/data_set/list_new')
appbuilder.add_view(DataSetView, "Data Sets Admin", category="Data", href='/data_set/list/')
appbuilder.add_view_no_menu(DataSetAttachmentView)

