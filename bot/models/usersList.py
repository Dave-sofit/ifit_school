from sqlalchemy import Index

from bot.models.utils import ListTableWithArchive


class User(ListTableWithArchive):
    __tablename__ = 'usersList'


Index(name='ind_user_data_gin', expressions=User.data, postgresql_using="gin")
