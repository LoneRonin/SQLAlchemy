from orm_base import Base
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Course import Course
from typing import List
from datetime import time
from sqlalchemy.types import Time

class Section(Base):

    __tablename__ = "section"  # Give SQLAlchemy th name of the table.

    departmentAbbreviation: Mapped[str] = mapped_column('department_abbreviation', String(10), primary_key=True)

    course: Mapped["Course"] = relationship(back_populates="sections")

    courseNumber: Mapped[int] = mapped_column('course_number', Integer, primary_key=True)
    sectionNumber: Mapped[int] = mapped_column('section_number', Integer, nullable=False, primary_key=True)
    semester: Mapped[str] = mapped_column('semester', String(10), nullable=False, primary_key=True)
    sectionYear: Mapped[int] = mapped_column('section_year', Integer, nullable=False, primary_key=True)
    building: Mapped[str] = mapped_column('building', String(6), nullable=False)
    room: Mapped[int] = mapped_column('room', Integer, nullable=False)
    schedule: Mapped[str] = mapped_column('schedule', String(6), nullable=False)
    startTime: Mapped[time] = mapped_column('start_time', Time, nullable=False)
    instructor: Mapped[str] = mapped_column('instructor', String(80), nullable=False)

    __table_args__ = (UniqueConstraint("section_year", "semester", "schedule", "start_time", "building", "room",
                        name="section_uk_01"),
        UniqueConstraint("section_year", "semester", "schedule", "start_time", "instructor", name="section_uk_02"),
        ForeignKeyConstraint([departmentAbbreviation, courseNumber],
                                           [Course.departmentAbbreviation, Course.courseNumber]))

    def __init__(self, course: Course, sectionNumber: int, semester: str, sectionYear: int, building: str, room: int,
                 schedule: str, startTime, instructor: str):
        self.set_course(course)
        self.sectionNumber = sectionNumber
        self.semester = semester
        self.sectionYear = sectionYear
        self.building = building
        self.room = room
        self.schedule = schedule
        self.startTime = startTime
        self.instructor = instructor

    def set_course(self, course: Course):
        self.course = course
        self.departmentAbbreviation = course.departmentAbbreviation
        self.courseNumber = course.courseNumber

    def __str__(self):
        return f"Section {self.courseNumber} {self.sectionNumber} " \
               f"in {self.semester} {self.sectionYear} by {self.instructor} at {self.building} {self.room}, " \
               f"schedule {self.schedule} starting at {self.startTime}"
