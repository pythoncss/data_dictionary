import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from flask_appbuilder.models.mixins import AuditMixin
from datetime import datetime
from sqlalchemy.sql import func



class AuditMixinNullable(AuditMixin):

    created_on = sa.Column(sa.DateTime, default=func.now(), nullable=False)
    changed_on = sa.Column(sa.DateTime, default=func.now(), onupdate=datetime.now, 
    	nullable=True)

    @declared_attr
    def created_by_fk(self):
        return sa.Column(
            sa.Integer, sa.ForeignKey('ab_user.id'),
            default=self.get_user_id, nullable=True)

    @declared_attr
    def changed_by_fk(self):
        return sa.Column(
            sa.Integer, sa.ForeignKey('ab_user.id'),
            default=self.get_user_id, onupdate=self.get_user_id, nullable=True)

