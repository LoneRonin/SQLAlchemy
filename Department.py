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
    __tablename__ = "department"  # Give SQLAlchemy th name of the table.
    departmentName: Mapped[int] = mapped_column('department_name', String(50),
                                           nullable=False, primary_key=True)
    abbreviation: Mapped[str] = mapped_column('abbreviation', String(6), nullable=False)
    chairName: Mapped[str] = mapped_column('chair_name', String(80), nullable=False)
    building: Mapped[str] = mapped_column('building', String(10), nullable=False)
    office: Mapped[str] = mapped_column('office', Integer, nullable=False)
    description: Mapped[str] = mapped_column('description', String(80), nullable=False)
    # child class course
    majors: Mapped[List["Major"]] = relationship(back_populates="department")
    courses: Mapped[List["Course"]] = relationship(back_populates="department")
    # __table_args__ can best be viewed as directives that we ask SQLAlchemy to
    # send to the database.  In this case, that we want four separate uniqueness
    # constraints (candidate keys).
    __table_args__ = (UniqueConstraint("abbreviation", name="department_uk_01"),
                      UniqueConstraint("chair_name", name="department_uk_02"),
                      UniqueConstraint("building", "office", name="department_uk_03"),
                      UniqueConstraint("description", name="department_uk_04"))

    def add_course(self, course):
        if course not in self.courses:
            self.courses.add(course)            # I believe this will update the course as well.

    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)

    def get_courses(self):
        return self.courses

    def __init__(self, departmentName: str, abbreviation: str, chairName: str, building: str, office: int,
                 description: str):
        self.departmentName = departmentName
        self.abbreviation = abbreviation
        self.chairName = chairName
        self.building = building
        self.office = office
        self.description = description

    def __str__(self):
        return f"Department: {self.departmentName} Abbreviation: {self.abbreviation}\nChair Name: {self.chairName}" \
               f"\nBuilding: {self.building}, Office: {self.office}\n{self.description}\n" \
               f"Number Courses Offered:{len(self.courses)}"
