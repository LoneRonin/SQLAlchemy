from orm_base import Base
from sqlalchemy import UniqueConstraint, ForeignKey, Date, ForeignKeyConstraint, Integer, Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class Enrollment(Base):
    __tablename__ = "enrollment"

    enrollmentId: Mapped[int] = mapped_column('enrollment_id', Integer, Identity(start=1, cycle=True),
                                              primary_key=True)

    section: Mapped[List["Section"]] = relationship(back_populates="student")
    sectionId: Mapped[int] = mapped_column('section_id', ForeignKey("section.section_id"))

    student: Mapped[List["Student"]] = relationship(back_populates="section")
    studentId: Mapped[int] = mapped_column('student_id', ForeignKey("student.student_id"))

    type: Mapped[str] = mapped_column("type", String(50), nullable=False)

    __table_args__ = (UniqueConstraint("section_id", name="enrollment_uk_01"), ForeignKeyConstraint(["section_id"],
                                                            ["section.section_id"], name="enrollment_section_fk_01"),)
    __mapper_args__ = {"polymorphic_identity": "enrollment", "polymorphic_on": "type"}

    def __init__(self, student, section):
        self.student = student
        self.section = section
        self.student_id = student.studentId
        self.departmentAbbreviation = section.departmentAbbreviation
        self.courseNumber = section.courseNumber
        self.sectionNumber = section.sectionNumber
        self.semester = section.semester
        self.sectionYear = section.sectionYear

    def __str__(self):
        return f"Enrollment - student: {self.student} section: {self.section}"
