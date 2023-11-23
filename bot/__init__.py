from contextvars import ContextVar
from uuid import UUID
from json import JSONEncoder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings

emptyRef = UUID('00000000-0000-0000-0000-000000000000')


class SessionData:
    session: ContextVar[AsyncSession] = ContextVar('session', default=emptyRef)
    language: ContextVar[str] = ContextVar('language', default=settings.DEFAULT_CONTENT_LANGUAGE)


old_default = JSONEncoder.default


def new_default(self, obj):
    if isinstance(obj, UUID):
        return str(obj)
    return old_default(self, obj)


JSONEncoder.default = new_default
