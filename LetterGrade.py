from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped
from Enrollment import Enrollment

class LetterGrade(Enrollment):
    __tablename__ = "letter_grade"
    # I HAD put Integer after the table name, but apparently it picks that up from the parent PK.
    letterGradeId: Mapped[int] = mapped_column('letter_grade_id', ForeignKey("enrollment.enrollment_id",
                                                                             ondelete="CASCADE"), primary_key=True)
    minSatisfactory: Mapped[str] = mapped_column('min_satisfactory', String(2), CheckConstraint("min_satisfactory\
     IN('A', 'B', 'C', 'D', 'F')", name="letter_grade_min_satisfactory_constraint"), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "letter_grade"}

    def __init__(self, section, student, min_satisfactory: str):
        super().__init__(section, student)
        self.minSatisfactory = min_satisfactory

    def __str__(self):
        return f"LetterGrade Enrollment: {super().__str__()} Grade: {self.minSatisfactory}"
