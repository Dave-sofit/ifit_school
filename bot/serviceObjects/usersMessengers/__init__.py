# from uuid import UUID
# from pydantic import BaseModel
#
# from bot.common import MessengerTypes
# from bot.serviceObjects.utils import UuidBase, QueryParamFields
#
#
# class UserMessengerBase(BaseModel):
#     userUid: UUID
#     type: MessengerTypes
#     userMessengerId: int
#
#
# class UserMessengerIn(UserMessengerBase):
#     pass
#
#
# class UserMessengerOut(UserMessengerBase):
#     class Config:
#         from_attributes = True
#
#
# class UserMessengerQueryParamFields(QueryParamFields):
#     pass
