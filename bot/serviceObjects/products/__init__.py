from pydantic import BaseModel

from bot.serviceObjects.utils import UuidBase, QueryParamFields, SchemaDB


class ProductBase(BaseModel):
    name: str
    descriptions: str
    content: str
    certificate: str
    order: int


class ProductIn(ProductBase):
    pass


class ProductUpdate(ProductIn, UuidBase):
    pass


class ProductOut(ProductBase, UuidBase):
    class Config:
        from_attributes = True


class ProductQueryParamFields(QueryParamFields):
    pass


class ProductData(BaseModel):
    name: str
    descriptions: str
    content: str
    certificate: str
    order: int


class ProductDataT(BaseModel):
    pass


class ProductSchemaDB(SchemaDB):
    data: ProductData
    dataT: ProductDataT
