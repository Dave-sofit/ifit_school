from typing import List

from bot.models import Product as ProductDB
from bot.serviceObjects.products import ProductIn, ProductOut, ProductSchemaDB, \
    ProductQueryParamFields as QueryParamFields
from bot.serviceObjects.utils import ServiceObjectBase


class ProductMng(ServiceObjectBase):
    ClsDB = ProductDB
    Cls = ProductOut
    SchemaDB = ProductSchemaDB

    async def create(self, obj: ProductIn = None, notCommit: bool = False) -> ProductOut:
        return await super().create(obj=obj, notCommit=notCommit)

    async def get(self, objectDB=None, queryParams: QueryParamFields = None, **kwargs) -> ProductOut:
        return await super().get(objectDB=objectDB, queryParams=queryParams, **kwargs)

    async def getList(self, queryParams: QueryParamFields = None, order_by: dict = None, **kwargs) -> List[ProductOut]:
        return await super().getList(queryParams=queryParams, order_by=order_by, **kwargs)
