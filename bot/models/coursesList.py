from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy_utils import UUIDType

from bot.models.utils import ListTableWithArchive


class Course(ListTableWithArchive):
    __tablename__ = 'coursesList'
    productUid = Column(UUIDType(), ForeignKey('productsList.uid'), nullable=False)


Index('ind_course_data_gin', Course.data, postgresql_using="gin")
