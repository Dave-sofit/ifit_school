from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy_utils import UUIDType

from bot.models.utils import InfoRgTable


class Settlement(InfoRgTable):
    __tablename__ = 'settlementsInfoRg'
    createdOn = Column(TIMESTAMP(), default=datetime.utcnow, primary_key=True, nullable=False)
    courseUid = Column(UUIDType(), ForeignKey('coursesList.uid'), primary_key=True, nullable=False)
    userUid = Column(UUIDType(), ForeignKey('usersList.uid'), primary_key=True, nullable=False)
    amount = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f'{self.createdOn} - {self.courseUid} - {self.userUid} - {self.amount}'
