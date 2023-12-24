from datetime import datetime
from uuid import uuid4, UUID
from typing import Any, Sequence

from geoalchemy2.functions import GenericFunction
from sqlalchemy import Column, Boolean, PrimaryKeyConstraint, BigInteger, MetaData, TIMESTAMP, String, ForeignKey, \
    Identity, RowMapping, Row
from sqlalchemy import insert, update, delete, bindparam
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, QueryableAttribute
from sqlalchemy_utils import UUIDType, TranslationHybrid

from ..common import getLocale
from ..engine import getSession

metadata = MetaData()

Base = declarative_base()

translation_hybrid = TranslationHybrid(
    current_locale=getLocale,
    default_locale=lambda obj: obj.locale,
    default_value='{}'
)


class BaseTable(Base):
    __abstract__ = True
    __metadata__ = metadata

    @classmethod
    def _getattrFromColumnName(cls, name, default=...):
        for attr, column in inspect(cls).columns.items():
            if column.name == name:
                return getattr(cls, attr)

        if default is ...:
            raise KeyError
        else:
            return default

    @staticmethod
    async def execute(query) -> ChunkedIteratorResult:
        async with getSession() as session:
            res = await session.execute(query)
        return res

    @staticmethod
    async def scalar(query):
        async with getSession() as session:
            res = await session.scalar(query)

        return res

    @staticmethod
    async def commit(notCommit=False):
        if not notCommit:
            async with getSession() as session:
                try:
                    await session.commit()
                except:
                    await session.rollback()
                    raise

    @classmethod
    async def add_all(cls, objects: tuple, notCommit=True):
        getSession().add_all(objects)
        await cls.commit(notCommit)

    async def add(self, notCommit=True):
        getSession().add(self)
        await self.commit(notCommit)

    async def delete(self, notCommit=False):
        await getSession().delete(self)
        await self.commit(notCommit)

    @classmethod
    async def deleteList(cls, notCommit=False, **kwargs):
        for item in await cls.list(**kwargs):
            await item.delete(notCommit)

    @classmethod
    async def count(cls, **kwargs):
        return (await cls.execute(await cls.__queryNoRestriction(kwargs))).scalar_one_or_none().count()

    @classmethod
    async def exists(cls, **kwargs):
        return (await cls.execute(await cls.__queryNoRestriction(kwargs))).scalar_one_or_none() is not None

    @classmethod
    async def __queryNoRestriction(cls, kwargs):
        query = select(cls).filter_by(**cls.prepareFilter(noRestriction=True, **kwargs))
        return query

    @classmethod
    async def get(cls, **kwargs):
        filter_by = cls.prepareFilter(primaryOnly=True, **kwargs)
        if len(filter_by) > 0:
            return (await cls.execute(select(cls).filter_by(**filter_by))).scalars().unique().one_or_none()
        else:
            return None

    @classmethod
    async def list(cls, **kwargs):
        return (await cls.execute(await cls.__queryNoRestriction(kwargs))).scalars().unique().all()

    @classmethod
    async def first(cls, **kwargs):
        query = (await cls.__queryNoRestriction(kwargs)).limit(1)
        return (await cls.execute(query)).scalars().unique().one_or_none()

    @classmethod
    async def inList(cls, field, listFilter: []):
        query = select(cls).filter_by(**cls.prepareFilter()).where(
            cls._getattrFromColumnName(field).in_(listFilter))
        return (await cls.execute(query)).scalars().unique().all()

    # TODO хорошо бы причесать вызовы, in list убрать и интегрировать в другие
    #  пытаюсь сделать общий интегрированный фильтр, будет поддерживать where field = p1 and field1 in l1
    @classmethod
    async def filter(cls, query: select = None, order_by: dict | None = None, **kwargs) -> Sequence[
        Row | RowMapping | Any]:

        selectRow = kwargs.pop('selectRow', False)
        parameters = {}

        if query is None:
            query = select(cls)

        for k, v in kwargs.items():
            if isinstance(v, list):
                query = query.where(cls._getattrFromColumnName(k).in_(v))
            elif isinstance(v, dict):
                query = query.where(cls.__getattribute__(cls, k).op('@>')(v))
            elif isinstance(v, GenericFunction):
                query = query.where(v)
            else:
                parameters[k] = v

        for k, v in cls.prepareFilter(**parameters, noRestriction=True).items():
            if hasattr(cls, k):
                query = query.filter(getattr(cls, k).__eq__(v))

        if order_by is not None:
            for k, v in order_by.items():
                if isinstance(v, dict):
                    for k1, v1 in v.items():
                        if hasattr(cls, k1):
                            query = query.order_by(getattr(cls, k1).op('->')(v1))
                else:
                    query = query.order_by(v)

        if selectRow:
            return (await cls.execute(query)).all()
        else:
            return (await cls.execute(query)).scalars().unique().all()

    @classmethod
    def prepareFilter(cls, primaryOnly=False, noRestriction=False, **kwargs) -> dict:
        if kwargs is None:
            kwargs = {}

        filter_by = {}

        if noRestriction:
            primary_keys = []
            _columns = {}
        else:
            _inspect = inspect(cls)
            primary_keys = [key.name for key in _inspect.primary_key]
            _columns = _inspect.columns

        for k, v in kwargs.items():
            if noRestriction \
                    or k in primary_keys \
                    or (not primaryOnly and _columns[k].foreign_keys.__len__()) > 0:
                filter_by[k] = v

        if issubclass(cls, WithArchive) and 'archive' not in kwargs:
            filter_by['archive'] = False

        return filter_by

    @classmethod
    async def addFilterToJsonb(cls, attr: QueryableAttribute, attrName: str, attrValue: Any,
                               query: select = None) -> select:
        if query is None:
            query = select(cls)

        return query.where(attr.op('@>')({attrName: attrValue}))


class ColumnUidBigInt(BaseTable):
    __abstract__ = True
    uid = Column(BigInteger, autoincrement=True)


class Translated(BaseTable):
    __abstract__ = True
    # noinspection PyTypeChecker
    dataTranslations = Column(MutableDict.as_mutable(JSONB))
    locale = Column(String(5), default=getLocale)

    @declared_attr
    def dataT(self):
        return translation_hybrid(self.dataTranslations)

    def __repr__(self):
        return self.dataT


class WithCreating(BaseTable):
    __abstract__ = True
    createdOn = Column(TIMESTAMP(), default=datetime.utcnow)
    creatorUid = Column(UUIDType())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WithUID(BaseTable):
    __abstract__ = True
    uid = Column(UUIDType())

    @declared_attr
    def __table_args__(self):
        return (PrimaryKeyConstraint('uid'),
                )

    def __init__(self, *args, **kwargs):
        if 'uid' not in kwargs and hasattr(self, 'uid') and not isinstance(self, ColumnUidBigInt):
            kwargs['uid'] = uuid4()
        super().__init__(*args, **kwargs)

    @classmethod
    async def updateByUid(cls, uid: UUID, notCommit=False, **values):
        stmt = update(cls).where(cls.uid == uid).values(**values)

        await getSession().execute(stmt)

        await cls.commit(notCommit)


class Bulk(BaseTable):
    __abstract__ = True

    @classmethod
    async def addByList(cls, objs: list):
        if objs:
            await getSession().execute(insert(cls), objs)

    @classmethod
    async def updateByFilter(cls, objs: list, keys: dict):
        """Метод update не определяет первичные ключи, поэтому пришлось их пробрасывать
        возможно, в 2.0 будет работать"""

        stmt = update(cls)

        for k, v in keys.items():
            stmt = stmt.where(cls._getattrFromColumnName(k) == bindparam(v))
        await getSession().execute(stmt, objs)

    @classmethod
    async def deleteByFilter(cls, whereParams: list):
        stmt = delete(cls).execution_options(synchronize_session="fetch")

        for nameCol, operator, value in whereParams:
            stmt = stmt.where(cls._getattrFromColumnName(nameCol).op(operator)(value))

        await getSession().execute(stmt)

    @classmethod
    async def deleteList(cls, notCommit=False, **kwargs):
        for item in await cls.list(**kwargs):
            await item.delete(notCommit)


class ListTable(Translated, WithCreating, WithUID, Bulk):
    __abstract__ = True

    data = Column(JSONB)


class WithArchive(BaseTable):
    __abstract__ = True
    # TODO применить для archive частичный индекс ?!
    archive = Column(Boolean(), default=False)

    async def delete(self, notCommit=False):
        self.archive = True
        await self.add(notCommit)

    @classmethod
    async def get(cls, **kwargs):
        if 'archive' not in kwargs:
            kwargs['archive'] = False
        return await super().first(**kwargs)


class ListTableWithArchive(ListTable, WithArchive):
    __abstract__ = True


class ReplacingAdd(BaseTable):
    __abstract__ = True

    async def add(self, notCommit=True):
        await getSession().merge(self)
        await self.commit(notCommit)


class InfoRgTable(ReplacingAdd, Bulk):
    __abstract__ = True


class WithNumber(BaseTable):
    __abstract__ = True
    number = Column(BigInteger, Identity(start=1), index=True, insert_sentinel=True)


class WithFollower(BaseTable):
    __abstract__ = True

    objectUid = Column(UUIDType())

    @declared_attr
    def followerUid(self):
        return Column(UUIDType(), ForeignKey('customersList.uid'), index=True)

    @declared_attr
    def follower(self):
        return relationship('Customer', lazy='joined', foreign_keys=[self.followerUid])

    @declared_attr
    def __table_args__(self):
        return PrimaryKeyConstraint('objectUid', 'followerUid'),


class Document(ListTableWithArchive, WithNumber):
    __abstract__ = True
