from orm_base import Base
from sqlalchemy import Column, Integer, UniqueConstraint, Identity
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List                 # Use this for the list of Majors that this student has
from StudentMajor import StudentMajor
from Enrollment import Enrollment
from datetime import datetime

class Student(Base):
    """An individual who is currently enrolled or has explicitly stated an intent
    to enroll in one or more classes.  Said individuals may or may not be admitted
    to the university.  For instance, open enrollment students have not (yet) been
    admitted to the university, but they are still students."""
    __tablename__ = "student" # Give SQLAlchemy th name of the table.
    studentId: Mapped[int] = mapped_column('student_id', Integer, Identity(start=1, cycle=True),
                                           nullable=False, primary_key=True)
    lastName: Mapped[str] = mapped_column('last_name', String(50), nullable=False)
    firstName: Mapped[str] = mapped_column('first_name', String(50), nullable=False)
    eMail: Mapped[str] = mapped_column('e_mail', String(80), nullable=False)
    # __table_args__ can best be viewed as directives that we ask SQLAlchemy to
    # send to the database.  In this case, that we want two separate uniqueness
    # constraints (candidate keys).

    section: Mapped[List["Enrollment"]] = relationship(back_populates="student",
                                                        cascade="all, save-update, delete-orphan")
    major: Mapped[List["StudentMajor"]] = relationship(back_populates="student",
                                                        cascade="all, save-update, delete-orphan")

    __table_args__ = (UniqueConstraint("last_name", "first_name", name="students_uk_01"),
                      UniqueConstraint("e_mail", name="students_uk_02"))

    def __init__(self, last_name: str, first_name: str, e_mail: str):
        self.lastName = last_name
        self.firstName = first_name
        self.eMail = e_mail

    def add_major(self, m):
        """Add a new major to the student.  We are not actually adding a major directly
        to the student.  Rather, we are adding an instance of StudentMajor to the student.
        :param  major:  The Major that this student has declared.
        :return:        None
        """
        # Make sure that this student does not already have this major.
        for next_major in self.major:
            if next_major.m == m:
                return  # This student already has this major
        # Create the new instance of StudentMajor to connect this Student to the supplied Major.
        student_major = StudentMajor(self, m, datetime.now())

    #        major.students.append(student_major)                # Add this Student to the supplied Major.
    #        self.majors.append(student_major)                   # Add the supplied Major to this student.

    def remove_major(self, m):
        """
        Remove a major from the list of majors that a student presently has declared.
        Essentially, we are UNdeclaring the major.  A bit contrived, but this is for
        demonstration purposes.
        :param major:
        :return:
        """
        for next_major in self.major:
            # This item in the list is the major we are looking for for this student.
            if next_major.m == m:
                self.major.remove(next_major)
                return

    def add_section(self, s):
        """Add a new major to the student.  We are not actually adding a major directly
        to the student.  Rather, we are adding an instance of StudentMajor to the student.
        :param  major:  The Major that this student has declared.
        :return:        None
        """
        # Make sure that this student does not already have this major.
        for next_section in self.section:
            if next_section.s == s:
                return  # This student already has this major
        # Create the new instance of StudentMajor to connect this Student to the supplied Major.
        student_section = Enrollment(self, s)

    #        major.students.append(student_major)                # Add this Student to the supplied Major.
    #        self.majors.append(student_major)                   # Add the supplied Major to this student.

    def remove_section(self, s):
        """
        Remove a major from the list of majors that a student presently has declared.
        Essentially, we are UNdeclaring the major.  A bit contrived, but this is for
        demonstration purposes.
        :param major:
        :return:
        """
        for next_section in self.section:
            # This item in the list is the major we are looking for for this student.
            if next_section.s == s:
                self.section.remove(next_section)
                return

    def remove_enrollment(self, enrollment):
        self.remove_section

    def __str__(self):
        return f"Student id: {self.studentId} name: {self.lastName}, {self.firstName}\nEmail Address: {self.eMail}"
