from sqlalchemy import Index

from bot.models.utils import ListTableWithArchive


class Product(ListTableWithArchive):
    __tablename__ = 'productsList'


Index(name='ind_user_data_gin', expressions=Product.data, postgresql_using="gin")
