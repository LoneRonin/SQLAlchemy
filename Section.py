from orm_base import Base
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, CheckConstraint
from sqlalchemy import String, Integer, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Course import Course
from typing import List
from datetime import time
from Enrollment import Enrollment
from sqlalchemy.types import Time

class Section(Base):
    """An offering of a Course in a specific place and time."""
    __tablename__ = "section"
    course: Mapped["Course"] = relationship(back_populates="section")
    departmentAbbreviation: Mapped[str] = mapped_column("department_abbreviation",
                                                            primary_key=True)
    courseNumber: Mapped[int] = mapped_column("course_number",
                                                  primary_key=True)
    sectionNumber: Mapped[int] = mapped_column("section_number",
                                                   primary_key=True)
    semester: Mapped[str] = mapped_column("semester", String(20),
                                          CheckConstraint("semester IN('Fall', 'Spring', 'Winter',\
     'Summer I', 'Summer II', 'Summer III')", name="section_semester_constraint"),
                                              primary_key=True)
    sectionYear: Mapped[int] = mapped_column("section_year", nullable=False,
                                                 primary_key=True)
    building: Mapped[str] = mapped_column("building", String(10))
    room: Mapped[int] = mapped_column("room")
    schedule: Mapped[str] = mapped_column("schedule",
                                             CheckConstraint("schedule IN('MW', 'MWF', 'TuTh', 'F', 'S')",
                                                              name="section_schedule_constraint"))
    startTime: Mapped[time] = mapped_column("start_time")
    instructor: Mapped[str] = mapped_column("instructor", String(80))
    student: Mapped[List["Enrollment"]] = relationship(back_populates="section",
                                                            cascade="all, save-update, delete-orphan")

    __table_args__ = (UniqueConstraint("semester", "section_year", "schedule",
                                           "start_time", "building", "room",
                                           name="section_uk_01"),
                        UniqueConstraint("semester", "section_year", "schedule",
                                           "start_time", "instructor",
                                           name="section_uk_02"),
                        ForeignKeyConstraint([departmentAbbreviation, courseNumber],
                                               [Course.departmentAbbreviation,
                                                Course.courseNumber],
                                               name="section_course_fk_01"))

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

    def add_student(self, s):
        """Add a new major to the student.  We are not actually adding a major directly
        to the student.  Rather, we are adding an instance of StudentMajor to the student.
        :param  major:  The Major that this student has declared.
        :return:        None
        """
        # Make sure that this student does not already have this major.
        for next_student in self.student:
            if next_student.student == s:
                return  # This student already has this major
        # Create the new instance of StudentMajor to connect this Student to the supplied Major.
        section_student = Enrollment(s, self)

    #        major.students.append(student_major)                # Add this Student to the supplied Major.
    #        self.majors.append(student_major)                   # Add the supplied Major to this student.

    def remove_student(self, s):
        """
        Remove a major from the list of majors that a student presently has declared.
        Essentially, we are UNdeclaring the major.  A bit contrived, but this is for
        demonstration purposes.
        :param major:
        :return:
        """
        for next_student in self.student:
            # This item in the list is the major we are looking for this student.
            if next_student.student == s:
                self.student.remove(next_student)
                return

    def remove_enrollment(self, s):
        for next_student in self.student:
            # This item in the list is the major we are looking for this student.
            if next_student.student == s:
                self.student.remove(next_student)
                return

    def __str__(self):
        return f"Section {self.courseNumber} {self.sectionNumber} " \
               f"in {self.semester} {self.sectionYear} by {self.instructor} at {self.building} {self.room}, " \
               f"schedule {self.schedule} starting at {self.startTime}"
