from typing import List

from bot.models import Course as CourseDB, CourseSchedule as CourseScheduleDB
from bot.serviceObjects.courses import CourseIn, CourseOut, CourseSchemaDB, CourseScheduleOut, \
    CourseQueryParamFields as QueryParamFields, CourseScheduleQueryParamFields
from bot.serviceObjects.utils import ServiceObjectBase


class CourseMng(ServiceObjectBase):
    ClsDB = CourseDB
    Cls = CourseOut
    SchemaDB = CourseSchemaDB

    async def create(self, obj: CourseIn = None, notCommit: bool = False) -> CourseOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: QueryParamFields = None, **kwargs) -> CourseOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: QueryParamFields = None, order_by: dict = None, **kwargs) -> List[CourseOut]:
        return await super().getList(queryParams=queryParams, order_by=order_by, **kwargs)


class CourseScheduleMng(ServiceObjectBase):
    ClsDB = CourseScheduleDB
    Cls = CourseScheduleOut
    pkey = ['courseUid', 'startDate']

    async def create(self, obj: CourseIn = None, notCommit: bool = False) -> CourseScheduleOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: CourseScheduleQueryParamFields = None,
                  **kwargs) -> CourseScheduleOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: CourseScheduleQueryParamFields = None, order_by: dict = None, **kwargs) -> \
        List[CourseScheduleOut]:
        return await super().getList(queryParams=queryParams, order_by=order_by, **kwargs)
