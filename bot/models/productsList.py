from sqlalchemy import Index

from bot.models.utils import ListTableWithArchive


class Product(ListTableWithArchive):
    __tablename__ = 'productsList'


Index('ind_product_data_gin', Product.data, postgresql_using="gin")
