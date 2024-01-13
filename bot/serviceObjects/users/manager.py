from typing import List

from bot.models import User as UserDB
from bot.serviceObjects.users import UserIn, UserOut, UserSchemaDB, UserQueryParamFields
from bot.serviceObjects.utils import ServiceObjectBase, QueryParamFields


class UserMng(ServiceObjectBase):
    ClsDB = UserDB
    Cls = UserOut
    SchemaDB = UserSchemaDB

    async def create(self, obj: UserIn = None, notCommit: bool = False) -> UserOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: QueryParamFields = None, **kwargs) -> UserOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: UserQueryParamFields = None, order_by: dict | None = None, **kwargs) -> List[
        UserOut]:
        return await super().getList(queryParams=queryParams, query=None, order_by=order_by, **kwargs)

    async def first(self, queryParams: QueryParamFields = None, **kwargs) -> UserOut:
        return await super().first(queryParams=queryParams, **kwargs)
