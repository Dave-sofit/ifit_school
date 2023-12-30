# from sqlalchemy import Column, Enum, BigInteger, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy_utils import UUIDType
#
# from bot.common import MessengerTypes
#
# from bot.models.utils import InfoRgTable
#
#
# class UserMessenger(InfoRgTable):
#     __tablename__ = 'usersMessengersInfoRg'
#     userMessengerId = Column(BigInteger, primary_key=True, nullable=False)
#     type = Column(Enum(MessengerTypes), primary_key=True, nullable=False)
#     userUid = Column(UUIDType(), ForeignKey('usersList.uid'), index=True, nullable=False)
#
#     user = relationship('Company', lazy='joined', foreign_keys=[userUid])
