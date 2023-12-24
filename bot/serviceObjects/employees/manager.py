from typing import List

from bot.models import Employee as EmployeeDB
from bot.serviceObjects.employees import EmployeeIn, EmployeeOut, EmployeeSchemaDB, \
    EmployeeQueryParamFields as QueryParamFields
from bot.serviceObjects.utils import ServiceObjectBase


class EmployeeMng(ServiceObjectBase):
    ClsDB = EmployeeDB
    Cls = EmployeeOut
    SchemaDB = EmployeeSchemaDB

    async def create(self, obj: EmployeeIn = None, notCommit: bool = False) -> EmployeeOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: QueryParamFields = None, **kwargs) -> EmployeeOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: QueryParamFields = None, order_by: dict = None, **kwargs) -> List[EmployeeOut]:
        return await super().getList(queryParams=queryParams, order_by=order_by, **kwargs)
