from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, ForeignKey, SmallInteger, Date, Boolean, Table
from sqlalchemy.orm import relationship, backref
from citext import CIText
from flask import Markup, url_for
from flask_appbuilder.models.mixins import AuditMixin, FileColumn
from flask_appbuilder.filemanager import get_file_original_name


class TagValue(Model):
    tag_value_id = Column(Integer, primary_key=True)
    tag_value_name = Column(String(255))

    def __repr__(self):
        return '{}'.format(self.tag_value_name)


tag_values_table = Table('tag_values', Model.metadata, 
    Column('tag_id', Integer, ForeignKey('tag.tag_id'), primary_key=True),
    Column('tag_value_id', Integer, ForeignKey('tag_value.tag_value_id'), primary_key=True))


class Tag(Model):
    tag_id = Column(Integer, primary_key=True)
    tag_name = Column(String(255))
    tag_value = relationship("TagValue", secondary=lambda: tag_values_table, backref="tag")

    def __repr__(self):
        return '{}'.format(self.tag_name)


data_set_tags_table = Table('data_set_tags', Model.metadata, 
	Column('dataset_id', Integer, ForeignKey('data_set.dataset_id'), primary_key=True),
	Column('tag_id', Integer, ForeignKey('tag.tag_id'), primary_key=True))

data_set_tags_value_table = Table('data_set_tags_value', Model.metadata, 
    Column('dataset_id', Integer, ForeignKey('data_set.dataset_id'), primary_key=True),
    Column('tag_value_id', Integer, ForeignKey('tag_value.tag_value_id'), primary_key=True))


class DataSourceOwner(Model, AuditMixin):
    data_source_owner_id 	= Column(Integer, primary_key=True)
    data_source_owner 		= Column(String(40))
    data_source_owner_email = Column(String(40))

    def __repr__(self):
    	return self.data_source_owner

class DataSource(Model, AuditMixin):
    data_source_id = Column(Integer, primary_key=True)
    data_source_name = Column(CIText, nullable=False, unique=True)
    data_source_description = Column(Text)

    def __repr__(self):
            return "{}".format(self.data_source_name)

    def data_source_description_(self):
    	return Markup(self.data_source_description)

    def data_source_name_(self):
    	return Markup('<a href="/data_source/show/{}">{}</a>'.format(self.data_source_id, self.data_source_name))


class DataType(Model, AuditMixin):
    datatype_id = Column(SmallInteger, primary_key=True)
    datatype_name = Column(CIText, nullable=False, unique=True)
    datatype_description = Column(Text)

    def __repr__(self):
            return self.datatype_name

    def datatype_description_(self):
    	return Markup(self.datatype_description)

    def datatype_name_(self):
    	return Markup('<a href="/data_type/show/{}">{}</a>'.format(self.datatype_id, self.datatype_name))


class DataSet(Model, AuditMixin):
    dataset_id = Column(Integer, primary_key=True)
    dataset_name = Column(CIText(), nullable=False, unique=True)
    dataset_short_description = Column(String(127))
    dataset_description = Column(Text)
    dataset_schema = Column(String(127))
    storage_location_id = Column(SmallInteger, ForeignKey('storage_location.storage_location_id'), nullable=True)
    storage_location = relationship('StorageLocation')
    data_source_id = Column(Integer, ForeignKey('data_source.data_source_id'))
    data_source = relationship('DataSource')
    history_held_since = Column(Date)
    refresh_frequency_id = Column(SmallInteger, ForeignKey('refresh_frequency.refresh_frequency_id'), nullable=True)
    refresh_frequency = relationship('RefreshFrequency')
    recency_at_time_of_refresh = Column(Text)
    personally_identifiable_information = Column(Boolean, default=False)
    data_owner_id = Column(Integer, ForeignKey('data_source_owner.data_source_owner_id'), nullable=True)
    data_source_owner = relationship('DataSourceOwner')
    tags = relationship("Tag", secondary=lambda: data_set_tags_table, backref=backref("data_set", cascade="all,delete"))
    tags_value = relationship("TagValue", secondary=lambda: data_set_tags_value_table, backref=backref("data_set", cascade="all,delete"))
    approved = Column(Boolean, default=False)
    row_count = Column(String(120))
    primary_key = Column(String(120))
    data_supplier = Column(String(120))
    projects_using_this = Column(Text)
    position = Column(String(120))

    def __repr__(self):
            return self.dataset_name

    def tags_value_(self):
        return '{}:{}'.format(self.tag_value, self.tag_value.tag_value_name)

    def dataset_description_(self):
    	return Markup(self.dataset_description)

    def dataset_name_(self):
    	return Markup('<a href="/data_set/show/{}">{}</a>'.format(self.dataset_id, self.dataset_name))

    def data_source_owner_(self):
    	if self.data_owner_id is None:
    		return ''
    	return Markup('<a href="/data_source_owner/show/{}">{}</a>'.format(self.data_owner_id, self.data_source_owner))


class DatasetAttribute(Model, AuditMixin):
    column_name = Column(String(127), primary_key=True, nullable=False)
    dataset_id = Column(Integer, ForeignKey('data_set.dataset_id'), primary_key=True, nullable=False)
    dataset_name = relationship('DataSet')
    attribute_position = Column(SmallInteger)
    attribute_description = Column(Text)
    data_type_id = Column(SmallInteger, ForeignKey('data_type.datatype_id'))
    data_type = relationship('DataType')
    character_maximum_length = Column(SmallInteger)
    numeric_precision = Column(SmallInteger)
    numeric_scale = Column(SmallInteger)
    is_nullable = Column(Boolean, default=False)
    primary_key_position = Column(SmallInteger)
    count_of_unique_values = Column(String(120))
    count_of_null_values = Column(String(120))
    

    def __repr__(self):
            return '{}, {}'.format(self.column_name, self.dataset_name)

    def attribute_description_(self):
    	return Markup(self.attribute_description)


class StorageLocation(Model, AuditMixin):
    storage_location_id = Column(SmallInteger, primary_key=True)
    storage_location_name = Column(CIText, nullable=True, unique=True)
    storage_location_description = Column(Text)
    storage_type = Column(String(30))

    def __repr__(self):
            return self.storage_location_name

    def storage_location_description_(self):
    	return Markup(self.storage_location_description)

    def storage_location_name_(self):
    	return Markup('<a href="/storage_location/show/{}">{}</a>'.format(self.storage_location_id, self.storage_location_name))


class RefreshFrequency(Model, AuditMixin):
    refresh_frequency_id = Column(SmallInteger, primary_key=True)
    refresh_frequency_description = Column(CIText, nullable=False, unique=True)

    def __repr__(self):
            return self.refresh_frequency_description

    def refresh_frequency_description_(self):
    	return Markup('<a href="/refresh_frequency/show/{}">{}</a>'.format(self.refresh_frequency_id, 
    		self.refresh_frequency_description))


class DatasetView(Model):
    dataset_view_id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('data_set.dataset_id'), primary_key=True)
    data_set = relationship('DataSet')
    data_set_count = Column(Integer)

class DataSetFavorite(Model):
    dataset_fab_id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_fab_count = Column(Integer, default=0)
    dataset_id = Column(Integer, ForeignKey('data_set.dataset_id'), primary_key=True)
    data_set = relationship('DataSet')
    user_id = Column(Integer, ForeignKey('ab_user.id'), primary_key=True)
    user = relationship('User')


class DataSetAttachment(Model):
    dataset_attachment_id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_attachment_name = Column(String(255))
    dataset_attachment_file = Column(FileColumn, nullable=True)
    dataset_id = Column(Integer, ForeignKey("data_set.dataset_id"))
    data_set = relationship("DataSet")

    def __repr__(self):
        return self.dataset_attachment_file

    def download(self):
        return Markup(
            '<a href="'
            +url_for("DataSetAttachmentView.download", filename=str(self.dataset_attachment_file))
            +'">'+self.dataset_attachment_name+'</a>'
            )

    def file_name(self):
        return get_file_original_name(str(self.dataset_attachment_file))
