from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy_utils import UUIDType

from bot.models.utils import InfoRgTable


class ProductFAQ(InfoRgTable):
    __tablename__ = 'productsFAQInfoRg'
    productUid = Column(UUIDType(), ForeignKey('productssList.uid'), primary_key=True, nullable=False)
    number = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(150))
    answer = Column(String(250))

    def __repr__(self):
        return f'{self.productUid} - {self.number}'
