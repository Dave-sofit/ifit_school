from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy_utils import UUIDType

from bot.models.utils import InfoRgTable


class Settlement(InfoRgTable):
    __tablename__ = 'settlementsInfoRg'
    courseUid = Column(UUIDType(), ForeignKey('coursesList.uid'), primary_key=True, nullable=False)
    userUid = Column(UUIDType(), ForeignKey('usersList.uid'), primary_key=True, nullable=False)
    amount = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f'{self.courseUid} - {self.userUid} - {self.amount}'
