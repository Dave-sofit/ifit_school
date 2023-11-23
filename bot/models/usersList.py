from sqlalchemy import Index

from bot.models.utils import ListTableWithArchive


class User(ListTableWithArchive):
    __tablename__ = 'usersList'


Index('ind_user_data_gin', User.data, postgresql_using="gin")
