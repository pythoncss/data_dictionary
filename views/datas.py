from app import appbuilder
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .utils import DataSQLAInterface
from app.models.datas import (DataSource, DataType, DataSet, DatasetAttribute,
        StorageLocation, RefreshFrequency, DataSourceOwner, Tag, TagValue)


class ModelViewWithAudit(ModelView):
    _audit_columns=['created_on','changed_on','created_by','changed_by']
    add_exclude_columns = _audit_columns
    edit_exclude_columns = _audit_columns
    list_exclude_columns = _audit_columns
    show_include_colums = _audit_columns

class TagValueView(ModelViewWithAudit):
    datamodel = DataSQLAInterface(TagValue)
    list_columns = ['tag_value_name']
    list_title = "Tag Value"

class TagView(ModelViewWithAudit):
    datamodel = DataSQLAInterface(Tag)
    list_columns = ['tag_name']
    add_columns = edit_columns = ['tag_name']
    related_views = [TagValueView]
    list_title = "Tag"

class DataSourceOwnerView(ModelViewWithAudit):
    route_base  = "/data_source_owner"
    datamodel   = DataSQLAInterface(DataSourceOwner)
    label_columns = {
        'created_by_fk'             : 'Created by',
        'created_on'                : 'Created on',
        'data_source_owner'         : 'Data Owner',
        'data_source_owner_email'   : 'Data Owner Email',
    }
    list_columns = ['data_source_owner', 'data_source_owner_email']
    add_columns  = ['data_source_owner', 'data_source_owner_email']
    edit_columns = ['data_source_owner', 'data_source_owner_email']
    show_columns = ['data_source_owner', 'data_source_owner_email']


class DataSourceView(ModelViewWithAudit):
    route_base = "/data_source"
    datamodel = DataSQLAInterface(DataSource)

    label_columns = {
        'created_by_fk'            : 'Created by',
        'created_on'               : 'Created on',
        'data_source_description_' : 'Description',
        'data_source_name_'        : 'Name',
    }

    list_columns = ['data_source_name_',
                    'created_on', 'created_by_fk']

    show_columns = ['data_source_name_',
                    'created_on', 'created_by_fk', 'data_source_description_']

    description_columns = {
        'data_source_name'        : 'Write a data source name',
        'data_source_description' : 'Write a data source description'
    }

    add_template = "/datas/add_with_tinymce.html"

    edit_template = "/datas/edit_with_tinymce.html"


class DataTypeView(ModelViewWithAudit):
    route_base = "/data_type"
    datamodel = DataSQLAInterface(DataType)

    label_columns = {
        'created_by'            : 'Created by',
        'created_on_'           : 'Created on',
        'datatype_description_' : 'Description',
        'datatype_name_'        : 'Data Type',
    }

    list_columns = ['datatype_name_', 'datatype_description_', 'created_on', 'created_by']

    add_template = "/datas/add_with_tinymce.html"

    edit_template = "/datas/edit_with_tinymce.html"


class DataSetAttributeView(ModelViewWithAudit):
    route_base = "/dataset_attribute"
    datamodel = SQLAInterface(DatasetAttribute)
    list_title = "Dataset Attribute"

    label_columns = {
        'attribute_description_'  : 'Description',
        'column_name'             : 'Name',
        'attribute_position'      : 'Position',
        'data_type'               : 'Data Type',
        'dataset_name'            : 'Dataset'
    }
    add_columns =  ['dataset_name', 'column_name', 'attribute_description', 'attribute_position', 'data_type']
    edit_columns = ['dataset_name', 'column_name', 'attribute_description' , 'attribute_position', 'data_type']
    list_columns = ['column_name',  'attribute_description_' , 'attribute_position', 'data_type']
    show_columns = ['dataset_name', 'column_name', 'attribute_description_' , 'attribute_position', 'data_type']

    add_template = "/datas/add_with_tinymce.html"

    edit_template = "/datas/edit_with_tinymce.html"


class StorageLocationView(ModelViewWithAudit):
    route_base = "/storage_location"
    datamodel = DataSQLAInterface(StorageLocation)

    label_columns = {
        'storage_location_description_' : 'Location Description',
        'storage_location_name_'        : 'Location Name',
        'storage_type'                  : 'Type',
    }

    list_columns = ['storage_location_name_', 'storage_type']

    show_columns = ['storage_location_name_', 'storage_type', 'storage_location_description_']

    add_template = "/datas/add_with_tinymce.html"

    edit_template = "/datas/edit_with_tinymce.html"
    


class RefreshFrequencyView(ModelViewWithAudit):
    route_base = "/refresh_frequency"
    datamodel = DataSQLAInterface(RefreshFrequency)

    label_columns = {'refresh_frequency_description': 'Description'}
    list_columns = ['refresh_frequency_description_', 'created_by']


appbuilder.add_view(DataSourceView, "Data Sources", category="Data", category_icon="")
appbuilder.add_view(DataTypeView, "Data Types", category="Data")

appbuilder.add_view(StorageLocationView, "Storage Locations", category="Data")
appbuilder.add_view(RefreshFrequencyView, "Refresh Frequencies", category="Data")

appbuilder.add_view_no_menu(DataSetAttributeView, "DataSetAttributeView")
appbuilder.add_view(TagView, "Tag", category="Tag", category_icon="")
appbuilder.add_view_no_menu(TagValueView, "TagValueView")
appbuilder.add_view(DataSourceOwnerView, "Data Source Owner", category="Data")


