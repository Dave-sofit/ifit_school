from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy_utils import UUIDType

from bot.models.utils import ListTableWithArchive


class Course(ListTableWithArchive):
    __tablename__ = 'coursesList'
    productUid = Column(UUIDType(), ForeignKey('productssList.uid'), nullable=False)


Index(name='ind_user_data_gin', expressions=Course.data, postgresql_using="gin")
