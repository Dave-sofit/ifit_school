from enum import Enum


class UtilEnum(Enum):
    @classmethod
    def hasValue(cls, value) -> bool:
        return value in set(i.value for i in cls)


class MessengerTypes(str, UtilEnum):
    telegram = 'telegram'
    viber = 'viber'
    whatsapp = 'whatsapp'
