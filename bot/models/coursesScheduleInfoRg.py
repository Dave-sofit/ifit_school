from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy_utils import UUIDType

from bot.models.utils import InfoRgTable


class CourseSchedule(InfoRgTable):
    __tablename__ = 'coursesScheduleInfoRg'
    courseUid = Column(UUIDType(), ForeignKey('coursesList.uid'), primary_key=True, nullable=False)
    startDate = Column(TIMESTAMP(), primary_key=True, nullable=False)

    def __repr__(self):
        return f'{self.courseUid} - {self.startDay}'
