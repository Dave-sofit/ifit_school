from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB


class EmployeeBase(BaseModel):
    firstName: str
    lastName: str | None = None
    descriptions: str | None = None


class EmployeeIn(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase, UuidBase):
    fullName: str | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fullName = f'{self.firstName} {self.lastName}'

    class Config:
        from_attributes = True


class EmployeeQueryParamFields(QueryParamFields):
    pass


class EmployeeData(BaseModel):
    firstName: str
    lastName: str
    descriptions: str


class EmployeeDataT(BaseModel):
    pass


class EmployeeSchemaDB(SchemaDB):
    data: EmployeeData
    dataT: EmployeeDataT
