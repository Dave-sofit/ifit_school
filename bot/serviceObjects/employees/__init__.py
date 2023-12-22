from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB


class EmployeeBase(BaseModel):
    firstName: str
    lastName: str
    description: str


class EmployeeIn(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase, UuidBase):
    class Config:
        from_attributes = True


class EmployeeQueryParamFields(QueryParamFields):
    pass


class EmployeeData(BaseModel):
    firstName: str
    lastName: str
    description: str


class EmployeeDataT(BaseModel):
    pass


class EmployeeSchemaDB(SchemaDB):
    data: EmployeeData
    dataT: EmployeeDataT
