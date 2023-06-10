from orm_base import Base
from sqlalchemy import UniqueConstraint, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
# We canNOT import Student and Major here because Student and Major
# are both importing StudentMajor.  So we have to go without the
# ability to validate the Student or Major class references in
# this class.  Otherwise, we get a circular import.
# from Student import Student
# from Major import Major
from datetime import datetime

class Enrollment(Base):
    __tablename__ = "enrollment"

    section: Mapped["Section"] = relationship(back_populates="student")
    student: Mapped["Student"] = relationship(back_populates="section")

    sectionId: Mapped[int] = mapped_column('section_id', ForeignKey("sections.section_id"), primary_key=True)
    studentId: Mapped[int] = mapped_column('student_id', ForeignKey("students.student_id"), primary_key=True)

    def __init__(self, student, section):
        self.student = student
        self.section = section
        self.student_id = student.studentID
        self.section_id = section.sectionID

    def __str__(self):
        return f"Enrollment - student: {self.student} section: {self.section}"
