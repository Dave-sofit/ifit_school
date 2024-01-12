from datetime import date
from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB


class UserBase(BaseModel):
    phone: str
    messengerId: int
    firstName: str | None = None
    lastName: str | None = None
    secondName: str | None = None
    nameEnglish: str | None = None
    birthday: date | None = None
    city: str | None = None
    crmId: str | None = None


class UserIn(UserBase):
    pass


class UserOut(UserBase, UuidBase):
    class Config:
        from_attributes = True


class UserQueryParamFields(QueryParamFields):
    pass


class UserData(BaseModel):
    phone: str
    messengerId: int
    firstName: str
    lastName: str
    secondName: str
    nameEnglish: str
    city: str


class UserDataT(BaseModel):
    pass


class UserSchemaDB(SchemaDB):
    data: UserData
    dataT: UserDataT
