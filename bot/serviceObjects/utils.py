from abc import ABCMeta
from typing import List, Dict, Any
from uuid import UUID
from collections.abc import KeysView

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement, WKBElement
from geoalchemy2.shape import to_shape
from geoalchemy2.comparator import Comparator
from pydantic import BaseModel, constr
from shapely import geometry
from sqlalchemy import select, func
from sqlalchemy.engine.row import Row

from ..common import LocalException
from ..common.enums import UtilEnum
from ..models import BaseTable
from .common import QueryParamFields


class SchemaDB(BaseModel):
    @classmethod
    def toDict(cls):
        result = {}
        schema = cls.model_json_schema()
        properties = schema.get('properties')
        defs = schema.get('$defs')

        for k in properties.keys():
            definition = properties.get(k).get('$ref').replace('#/$defs/', '')
            fieldList = [field for field in defs.get(definition).get('properties').keys()]

            result.update({k: fieldList})

        return result


class ServiceObjectBase(metaclass=ABCMeta):
    Cls: BaseModel = BaseModel
    ClsDB: BaseTable = BaseTable
    SchemaDB: SchemaDB = SchemaDB
    pkey: List = ['uid']
    exportingFields: set = set()
    _objectDB = None

    def __init__(self, **kwargs):
        if 'responseModel' in kwargs:
            self.Cls = kwargs['responseModel']

    @classmethod
    def getType(cls, typeOrMode):
        ...

    @classmethod
    async def updateByObjectIn(cls, objectIn: BaseModel, kwargs: Dict):
        if objectIn:
            kwargs.update(**objectIn.model_dump(exclude_none=True))

    async def commonHandler(self, queryParams=None):
        modelSchema = self.Cls.model_json_schema()
        if queryParams and queryParams.fields:
            requiredFields = modelSchema.get('required')
            if requiredFields is None:
                requiredFields = []
            self.exportingFields = set(queryParams.fields.replace(' ', '').split(',') + requiredFields)
        else:
            self.exportingFields = set(modelSchema.get('properties'))

    async def _getObjPK(self, obj: BaseModel | BaseTable) -> dict:
        return {k: getattr(obj, k) for k in self.pkey if hasattr(obj, k)}

    async def _get(self, objectDB=None, noneable=False, **kwargs) -> None:
        if objectDB is None:
            objectDB = await self.ClsDB.get(**{k: v for k, v in kwargs.items() if k in self.pkey})
            if objectDB is None and not noneable:
                raise LocalException(status=404, location=__name__,
                                     message=f'object not found ({"" if self.ClsDB is None else self.ClsDB.__name__})',
                                     type=str(self))
        self._objectDB = objectDB
        return objectDB

    async def _receiveResult(self, val: BaseTable | Dict | None = None) -> BaseModel | BaseTable | None:
        if self.Cls is None:
            if val:
                return val
            else:
                return self._objectDB

        if val is None:
            val = self._objectDB

        if self.Cls is None:
            return val
        elif hasattr(self.Cls.Config, 'from_attributes') and self.Cls.Config.from_attributes:
            return await self._from_orm(val)
        elif isinstance(val, Dict):
            return await self._from_orm(**val)
        else:
            return None

    def _getSaveData(self, kwargs):
        dataDict = {}
        for k, v in self.SchemaDB.toDict().items():
            if hasattr(self.ClsDB, k):
                v2 = {v1: kwargs[v1] for v1 in v if v1 in kwargs}
                if len(v2) != 0:
                    dataDict.update({k: v2})

        for k, v in kwargs.items():
            if hasattr(self.ClsDB, k):
                dataDict.update(k=v)

        return {k: v for k, v in kwargs.items() if hasattr(self.ClsDB, k) and k != 'coordinates'} | dataDict

    def _fillObj(self, kwargs):
        fillProperties(self._objectDB, self._getSaveData(kwargs))

    async def _getObjDict(self, obj: BaseModel = None) -> Dict:
        objDbDict = {k: v for k, v in obj.model_dump().items()}
        for k, v in self.SchemaDB.toDict().items():
            if hasattr(self.ClsDB, k):
                v2 = {v1: objDbDict[v1] for v1 in v if objDbDict.get(v1) is not None}
                if len(v2) != 0:
                    objDbDict.update({k: v2})

        return {k: v for k, v in objDbDict.items() if hasattr(self.ClsDB, k)}

    async def _getObjDbDict(self, obj: BaseTable, constraintFields: set | None = None) -> Dict:
        objDict = {}
        if hasattr(obj, 'data') and isinstance(obj.data, Dict):
            attrs = await intersection(obj.data.keys(), constraintFields)
            fillProperties(objDict, obj.data, attrs)

        if hasattr(obj, 'dataT') and isinstance(obj.dataT, Dict):
            attrs = await intersection(obj.dataT.keys(), constraintFields)
            fillProperties(objDict, obj.dataT, attrs)

        attrs = await intersection(obj.__dict__.keys(), constraintFields)
        for attr in attrs:
            objAttr = getattr(obj, attr)
            if isinstance(objAttr, BaseTable):
                objDict[attr] = await self._getObjDbDict(objAttr)
            elif isinstance(objAttr, WKBElement) or isinstance(objAttr, WKTElement):
                objDict[attr] = decodeGeoData(objAttr)
            else:
                objDict[attr] = objAttr

        return objDict

    async def _to_orm(self, obj: BaseModel | None = None) -> BaseTable | None:
        if obj is None:
            return None

        return self.ClsDB(**(await self._getObjDict(obj=obj)))

    async def _from_orm(self, obj: BaseTable | Dict | None = None) -> BaseModel | None:
        if obj is None:
            return None
        elif isinstance(obj, Dict):
            return self.Cls.model_validate(**obj)
        else:
            return self.Cls.model_validate(await self._getObjDbDict(obj, self.exportingFields))

    async def _commonFuncByList(self, listK: list, funct: Any) -> None:
        commit = False
        for k in listK:
            await funct(notCommit=True, **k.dict())
            commit = True
        if commit:
            await self.ClsDB.commit()

    async def create(self, obj: BaseModel = None, notCommit: bool = False):
        self._objectDB = await self._to_orm(obj)
        await self._objectDB.add(notCommit)
        await self._objectDB.commit(notCommit)
        if not notCommit:  # если не закоммитили, то и получать из базы нечего
            pk = await self._getObjPK(self._objectDB)
            await self._get(**pk)
        return await self._receiveResult()

    async def createObjects(self, objList: List[BaseModel], notCommit: bool = False) -> tuple[BaseModel | BaseTable | None]:
        if len(objList) > 0:
            objectsDB = tuple(await self._to_orm(obj) for obj in objList)
            await self.ClsDB.add_all(objectsDB, notCommit)
        else:
            objectsDB = tuple()

        return tuple(await self._receiveResult(objDB) for objDB in objectsDB)

    async def update(self, objectIn: BaseModel = None, objectDB: BaseTable = None, notCommit: bool = False, **kwargs):
        await self.updateByObjectIn(objectIn, kwargs)

        await self._get(objectDB, **kwargs)

        self._fillObj(kwargs)

        await self._objectDB.add(notCommit)

        result = await self._receiveResult()

        await self._objectDB.commit(notCommit)

        return result

    async def get(self, objectDB=None, queryParams: QueryParamFields = None, noneable=False, **kwargs):
        await self.commonHandler(queryParams=queryParams)
        await self._get(objectDB, noneable=noneable, **kwargs)
        return await self._receiveResult()

    async def getList(self, queryParams: QueryParamFields = None, query: select = None, order_by: dict | None = None, **kwargs):
        await self.commonHandler(queryParams=queryParams)
        items, total = await self.ClsDB.filter(query, order_by, **kwargs)
        receiveItems = [await self._receiveResult(i) for i in items]
        return receiveItems

    async def first(self, queryParams: QueryParamFields = None, query: select = None, **kwargs):
        await self.commonHandler(queryParams=queryParams)
        objsDB = await self.ClsDB.filter(query=query, **kwargs)
        if len(objsDB) > 0:
            return await self._receiveResult(objsDB[0])
        else:
            return None

    async def delete(self, objectIn: BaseModel = None, objectDB=None, **kwargs) -> None:
        await self.updateByObjectIn(objectIn, kwargs)

        if kwargs.get('byList'):
            await self._commonFuncByList(kwargs['list'], self.delete)
            return None

        await self._get(objectDB, **kwargs)
        await self._objectDB.delete()


class ServiceObjectGeo(ServiceObjectBase):
    async def _getObjDict(self, obj: BaseModel | None = None) -> Dict:
        return await self.encodeGeoData(await super()._getObjDict(obj=obj))

    async def encodeGeoData(self, kwargs: Dict) -> Dict:
        # noinspection PyProtectedMember
        for column in self.ClsDB.__dict__.get('__table__').c._collection:
            if isinstance(column[1].type, Geometry):
                geo = kwargs.get(column[0])
                if geo is not None:
                    kwargs[column[0]] = WKTElement(geo, srid=4326)

        return kwargs

    # async def update(self, objectIn: BaseModel = None, notCommit: bool = False, **kwargs):
    #     await self.encodeGeoData(objectIn)
    #     return await super().update(objectIn=objectIn, notCommit=False, **kwargs)

    async def orderByDistanceCentroid(self, latitude: float, longitude: float) -> dict:
        point = func.ST_SetSRID(func.ST_Point(longitude, latitude), 4326)
        return dict(point=Comparator.distance_centroid(self.ClsDB.coordinates, point))


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class UuidBase(BaseModel):
    uid: UUID


def decodeGeoData(v) -> dict | None:
    v = geometry.mapping(to_shape(v))
    if v.get('type') == 'Point':
        coordinates = v.get('coordinates')
        return {'latitude': coordinates[1], 'longitude': coordinates[0]}
    else:
        return None


def fillProperties(receiver, source, properties=None, exceptions=()) -> object:
    if properties is None:
        properties = source.keys()
    for attr in [a for a in properties if not a.startswith('_') and a not in exceptions]:
        if type(source) is dict or type(source) is Row:
            val = source[attr]
        else:
            val = getattr(source, attr)

        if isinstance(val, WKBElement) or isinstance(val, WKTElement):
            val = decodeGeoData(val)

        if type(receiver) is dict:
            receiver[attr] = val
        else:
            setattr(receiver, attr, val)

    return receiver


async def intersection(fields: List | KeysView, constraintFields: set | None = None) -> set:
    fieldsSet = set(fields)
    if constraintFields is None or len(constraintFields) == 0:
        return fieldsSet
    else:
        return fieldsSet.intersection(constraintFields)


class ListModelBase(BaseModel):
    name: constr(max_length=100)
    description: constr(max_length=1000) | None = ''


class ValidatorType(BaseModel, metaclass=ABCMeta):
    type: UtilEnum

    class Checker:
        enumValue = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = self.Checker.enumValue

    @classmethod
    def typeValid(cls, t):
        enumValue = cls.Checker.enumValue
        enumType = type(enumValue)
        return enumType.hasValue(t) and enumType(t) == enumValue

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        inPar = v

        isDict = isinstance(inPar, dict)
        if isDict:
            if 'type' not in inPar:
                raise TypeError('"type" not found')
        elif not hasattr(inPar, 'type'):
            hasData = hasattr(v, 'data')
            if hasData and 'type' in v.data:
                inPar = v.data
            else:
                raise TypeError('"type" not found')

        estType = inPar['type']

        if cls.typeValid(estType):
            if isDict:
                return cls(**v)
            else:
                # по идее тут не только ОРМ может быть, но пока так
                return cls.model_validate(v)

        raise ValueError(f'wrong type {estType}, estimate type {cls.Checker.enumValue}')

    class Config:
        from_attributes = True
