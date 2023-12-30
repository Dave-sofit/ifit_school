# from typing import List
#
# from bot.models import UserMessenger as UserMessengerDB
# from bot.serviceObjects.usersMessengers import UserMessengerIn, UserMessengerOut, UserMessengerQueryParamFields
# from bot.serviceObjects.utils import ServiceObjectBase, QueryParamFields
#
#
# class UserMessengerMng(ServiceObjectBase):
#     ClsDB = UserMessengerDB
#     Cls = UserMessengerOut
#     pkey = ['userMessengerId', 'type']
#
#     async def create(self, obj: UserMessengerIn = None, notCommit: bool = False) -> UserMessengerOut:
#         return await super().create(obj=obj, notCommit=notCommit)
#
#     async def get(self, objectDB=None, queryParams: QueryParamFields = None, noneable=False,
#                   **kwargs) -> UserMessengerOut:
#         return await super().get(objectDB=objectDB, queryParams=queryParams, noneable=noneable, **kwargs)
#
#     async def getList(self, queryParams: UserMessengerQueryParamFields = None, order_by: dict | None = None,
#                       **kwargs) -> List[
#         UserMessengerOut]:
#         return await super().getList(queryParams=queryParams, query=None, order_by=order_by, **kwargs)
