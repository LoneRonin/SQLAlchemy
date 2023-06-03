from sqlalchemy import Column, Integer, String, Time, create_engine, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKeyConstraint, PrimaryKeyConstraint
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

if TYPE_CHECKING:
    from Course import Course

class Section(Base):
    __tablename__ = 'sections'

    departmentAbbreviation: Mapped[str] = mapped_column('department_abbreviation', String(10),
                                                        ForeignKey("departments.abbreviation"), primary_key=True)
    courseNumber: Mapped[int] = mapped_column('course_number', Integer, ForeignKey("courses.courseNumber"),
                                              primary_key=True)
    sectionNumber: Mapped[int] = mapped_column('section_number', Integer, nullable=False, primary_key=True)
    semester: Mapped[str] = mapped_column('semester', String(10), nullable=False, primary_key=True)
    sectionYear: Mapped[int] = mapped_column('section_year', Integer, nullable=False, primary_key=True)
    building: Mapped[str] = mapped_column('building', String(6), nullable=False)
    room: Mapped[int] = mapped_column('room', Integer, nullable=False)
    schedule: Mapped[str] = mapped_column('schedule', String(6), nullable=False)
    startTime: Mapped = mapped_column('start_time', Time, nullable=False)
    instructor: Mapped = mapped_column('instructor', String(80), nullable=False)

    course: Mapped["Course"] = relationship(back_populates="sections")
    #course = relationship("Course", back_populates="sections")

    __table_args__ = (
        CheckConstraint("section_year", "semester", "schedule", "start_time", "building", "room",
                        name='sections_uk_01'),
        CheckConstraint("section_year", "semester", "schedule", "start_time", "instructor", name='sections_uk_02')
        #CheckConstraint("semester IN ('Fall', 'Spring', 'Winter', 'Summer I', 'Summer II')", name='sections_uk_01'),
        #CheckConstraint("building IN ('VEC', 'ECS', 'EN2', 'EN3', 'EN4', 'ET', 'SSPA')", name='sections_uk_02'),
        #CheckConstraint("schedule IN ('MW', 'TuTh', 'MWF', 'F', 'S')", name='sections_uk_03'),
    )

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

    def set_course(self, course: 'Course'):
        self.course = course
        self.courseNumber = course.courseNumber

    def __str__(self):
        return f"Section {self.courseNumber} {self.sectionNumber} " \
               f"in {self.semester} {self.sectionYear} by {self.instructor} at {self.building} {self.room}, " \
               f"schedule {self.schedule} starting at {self.startTime}"
