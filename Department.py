from orm_base import Base
from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class Department(Base):
    """An individual who is currently enrolled or has explicitly stated an intent
    to enroll in one or more classes.  Said individuals may or may not be admitted
    to the university.  For instance, open enrollment students have not (yet) been
    admitted to the university, but they are still students."""
    __tablename__ = "departments"  # Give SQLAlchemy th name of the table.
    department_name: Mapped[int] = mapped_column('department_name', String(50),
                                           nullable=False, primary_key=True)
    abbreviation: Mapped[str] = mapped_column('abbreviation', String(6), nullable=False)
    chair_name: Mapped[str] = mapped_column('chair_name', String(80), nullable=False)
    building: Mapped[str] = mapped_column('building', String(10), nullable=False)
    office: Mapped[str] = mapped_column('office', Integer, nullable=False)
    description: Mapped[str] = mapped_column('description', String(80), nullable=False)
    # child class course
    courses: Mapped[List["Course"]] = relationship(back_populates="department")
    # __table_args__ can best be viewed as directives that we ask SQLAlchemy to
    # send to the database.  In this case, that we want four separate uniqueness
    # constraints (candidate keys).
    __table_args__ = (UniqueConstraint("abbreviation", name="departments_uk_01"),
                      UniqueConstraint("chair_name", name="departments_uk_02"),
                      UniqueConstraint("building", "office", name="departments_uk_03"),
                      UniqueConstraint("description", name="departments_uk_04"))

    def __init__(self, department_name: str, abbreviation: str, chair_name: str, building: str, office: int,
                 description: str):
        self.department_name = department_name
        self.abbreviation = abbreviation
        self.chair_name = chair_name
        self.building = building
        self.office = office
        self.description = description

    def __str__(self):
        return f"Department: {self.department_name} Abbreviation: {self.abbreviation}\nChair Name: {self.chair_name}" \
               f"\nBuilding: {self.building}, Office: {self.office}\n{self.description}\n" \
               f"Number Courses Offered:{len(self.courses)}"
    