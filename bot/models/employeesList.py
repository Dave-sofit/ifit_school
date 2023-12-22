from sqlalchemy import Index

from bot.models.utils import ListTableWithArchive


class Employee(ListTableWithArchive):
    __tablename__ = 'employeesList'
    name = None


Index('ind_employee_data_gin', Employee.data, postgresql_using="gin")
