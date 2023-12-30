from uuid import UUID
from typing import List
from datetime import datetime

from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB
from bot.serviceObjects.employees import EmployeeOut
from bot.serviceObjects.users import UserOut


class CourseBase(BaseModel):
    name: str
    productUid: UUID
    price: int = 0
    descriptions: str | None = ''
    exam: str | None = ''
    location: str | None = ''
    crmId: str


class CourseIn(CourseBase):
    employeeUids: List[UUID] | None


class CourseOut(CourseBase, UuidBase):
    employees: List[EmployeeOut] | None = None

    class Config:
        from_attributes = True


class CourseQueryParamFields(QueryParamFields):
    pass


class CourseData(BaseModel):
    name: str
    productUid: UUID
    employeeUids: List[UUID]
    price: int
    descriptions: str
    exam: str
    location: str
    crmId: str


class CourseDataT(BaseModel):
    pass


class CourseSchemaDB(SchemaDB):
    data: CourseData
    dataT: CourseDataT


class CourseScheduleBase(BaseModel):
    courseUid: UUID
    startDate: datetime


class CourseScheduleIn(CourseScheduleBase):
    pass


class CourseScheduleOut(CourseScheduleBase):
    class Config:
        from_attributes = True


class CourseScheduleQueryParamFields(QueryParamFields):
    pass


class CourseApplicationBase(BaseModel):
    courseUid: UUID
    userUid: UUID
    startDate: datetime


class CourseApplicationIn(CourseApplicationBase):
    pass


class CourseApplicationOut(CourseApplicationBase):
    course: CourseOut
    user: UserOut

    class Config:
        from_attributes = True


class CourseApplicationQueryParamFields(QueryParamFields):
    pass
