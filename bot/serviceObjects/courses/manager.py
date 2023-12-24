from typing import List

from bot.models import Course as CourseDB
from bot.serviceObjects.courses import CourseIn, CourseOut, CourseSchemaDB, \
    CourseQueryParamFields as QueryParamFields
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
