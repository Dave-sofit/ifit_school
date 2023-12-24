from uuid import UUID
from typing import List
from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB
from bot.serviceObjects.employees import EmployeeOut


class CourseBase(BaseModel):
    name: str
    productUid: UUID
    price: int = 0
    descriptions: str | None = ''
    exam: str | None = ''
    location: str | None = ''


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


class CourseDataT(BaseModel):
    pass


class CourseSchemaDB(SchemaDB):
    data: CourseData
    dataT: CourseDataT
