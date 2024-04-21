from typing import List
from datetime import datetime

from sqlalchemy import select

from bot.models import Course as CourseDB, CourseSchedule as CourseScheduleDB, CourseApplication as CourseApplicationDB
from bot.serviceObjects.courses import CourseIn, CourseOut, CourseSchemaDB, CourseQueryParamFields as QueryParamFields
from bot.serviceObjects.courses import CourseScheduleIn, CourseScheduleOut, CourseScheduleQueryParamFields
from bot.serviceObjects.courses import CourseApplicationIn, CourseApplicationOut, CourseApplicationQueryParamFields

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

    async def create(self, obj: CourseScheduleIn = None, notCommit: bool = False) -> CourseScheduleOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: CourseScheduleQueryParamFields = None,
                  **kwargs) -> CourseScheduleOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: CourseScheduleQueryParamFields = None, order_by: dict = None, **kwargs) -> \
            List[CourseScheduleOut]:

        query = select(self.ClsDB).where(self.ClsDB.startDate > datetime.utcnow())
        return await super().getList(queryParams=queryParams, query=query, order_by=order_by, **kwargs)


class CourseApplicationMng(ServiceObjectBase):
    ClsDB = CourseApplicationDB
    Cls = CourseApplicationOut
    pkey = ['courseUid', 'userUid', 'startDate']

    async def create(self, obj: CourseApplicationIn = None, notCommit: bool = False) -> CourseApplicationOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: CourseApplicationQueryParamFields = None,
                  **kwargs) -> CourseApplicationOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: CourseApplicationQueryParamFields = None, order_by: dict = None, **kwargs) -> \
            List[CourseApplicationOut]:
        return await super().getList(queryParams=queryParams, order_by=order_by, **kwargs)
