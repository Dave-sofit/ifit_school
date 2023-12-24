from sqlalchemy import Index, cast, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, foreign
from sqlalchemy_utils import UUIDType

from bot.models.utils import ListTableWithArchive

from bot.models.employeesList import Employee
from bot.models.productsList import Product


class Course(ListTableWithArchive):
    __tablename__ = 'coursesList'
    product = relationship("Product", lazy='joined', viewonly=True,
                           primaryjoin=lambda: Product.uid == foreign(
                               Course.data.cast(JSONB)["productUid"].astext.cast(UUIDType)))


employees = select(
    cast(func.jsonb_array_elements_text(Course.data.op('->')('employeeUids')), UUID).label("employeeUid"),
    Course.uid.label("courseUid")).alias()

# noinspection PyTypeChecker
Course.employees = relationship(Employee, lazy='joined', viewonly=True, secondary=employees,
                                primaryjoin=employees.c.courseUid == Course.uid,
                                secondaryjoin=employees.c.employeeUid == Employee.uid)

Index('ind_course_data_gin', Course.data, postgresql_using="gin")
