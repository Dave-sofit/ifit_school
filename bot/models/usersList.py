from sqlalchemy import Column, Index, TIMESTAMP

from bot.models.utils import ListTableWithArchive


class User(ListTableWithArchive):
    __tablename__ = 'usersList'


Index('ind_user_data_gin', User.data, postgresql_using="gin")
