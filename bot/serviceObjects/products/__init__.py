from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB


class ProductBase(BaseModel):
    name: str
    crmId: str


class ProductIn(ProductBase):
    pass


class ProductOut(ProductBase, UuidBase):
    class Config:
        from_attributes = True


class ProductQueryParamFields(QueryParamFields):
    pass


class ProductData(BaseModel):
    name: str
    crmId: str


class ProductDataT(BaseModel):
    pass


class ProductSchemaDB(SchemaDB):
    data: ProductData
    dataT: ProductDataT