from uuid import UUID

from pydantic import BaseModel


class FileOut(BaseModel):
    fileName: str
    url: str


class QueryParamFields(BaseModel):
    fields: str | None = None


class QueryParamCreator(BaseModel):
    creatorUid: UUID | None = None
