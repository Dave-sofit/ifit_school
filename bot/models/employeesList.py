from sqlalchemy import Index

from bot.models.utils import ListTableWithArchive


class Employee(ListTableWithArchive):
    __tablename__ = 'employeesList'


Index(name='ind_user_data_gin', expressions=Employee.data, postgresql_using="gin")
