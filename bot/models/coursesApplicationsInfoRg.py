from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from bot.models.utils import InfoRgTable


class CourseApplication(InfoRgTable):
    __tablename__ = 'coursesApplicationsInfoRg'
    courseUid = Column(UUIDType(), ForeignKey('coursesList.uid'), primary_key=True, nullable=False)
    userUid = Column(UUIDType(), ForeignKey('usersList.uid'), primary_key=True, nullable=False)
    startDate = Column(TIMESTAMP(), primary_key=True, nullable=False)

    course = relationship('Course', lazy='joined', foreign_keys=[courseUid])
    user = relationship('User', lazy='joined', foreign_keys=[userUid])

    def __repr__(self):
        return f'{self.courseUid} - {self.userUid}'
