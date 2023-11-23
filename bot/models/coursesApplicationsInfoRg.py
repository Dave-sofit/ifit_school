from sqlalchemy import Column, ForeignKey
from sqlalchemy_utils import UUIDType

from bot.models.utils import InfoRgTable


class CourseApplication(InfoRgTable):
    __tablename__ = 'coursesApplicationsInfoRg'
    courseUid = Column(UUIDType(), ForeignKey('coursesList.uid'), primary_key=True, nullable=False)
    userUid = Column(UUIDType(), ForeignKey('usersList.uid'), primary_key=True, nullable=False)

    def __repr__(self):
        return f'{self.courseUid} - {self.userUid}'
