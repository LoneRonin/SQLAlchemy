import logging
from pprint import pprint

from sqlalchemy import select

from menu_definitions import menu_main, add_menu, delete_menu, list_menu, semester_menu, schedule_menu, debug_select
from db_connection import engine, Session
from orm_base import metadata
# Note that until you import your SQLAlchemy declarative classes, such as Student, Python
# will not execute that code, and SQLAlchemy will be unaware of the mapped table.
from Department import Department
from Course import Course
from Major import Major
from Student import Student
from Section import Section
from StudentMajor import StudentMajor
from Enrollment import Enrollment
from PassFail import PassFail
from LetterGrade import LetterGrade
from Option import Option
from Menu import Menu
import IPython

from datetime import time, datetime

def add(sess: Session):
    add_action: str = ''
    while add_action != add_menu.last_action():
        add_action = add_menu.menu_prompt()
        exec(add_action)


def delete(sess: Session):
    delete_action: str = ''
    while delete_action != delete_menu.last_action():
        delete_action = delete_menu.menu_prompt()
        exec(delete_action)


def list_objects(sess: Session):
    list_action: str = ''
    while list_action != list_menu.last_action():
        list_action = list_menu.menu_prompt()
        exec(list_action)

def add_student(session: Session):
    """
    Prompt the user for the information for a new student and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    unique_name: bool = False
    unique_email: bool = False
    lastName: str = ''
    firstName: str = ''
    email: str = ''
    # Note that there is no physical way for us to duplicate the student_id since we are
    # using the Identity "type" for studentId and allowing PostgreSQL to handle that.
    # See more at: https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-identity-column/
    while not unique_name or not unique_email:
        lastName = input("Student last name--> ")
        firstName = input("Student first name--> ")
        email = input("Student e-mail address--> ")
        name_count: int = session.query(Student).filter(Student.lastName == lastName,
                                                        Student.firstName == firstName).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a student by that name.  Try again.")
        if unique_name:
            email_count = session.query(Student).filter(Student.eMail == email).count()
            unique_email = email_count == 0
            if not unique_email:
                print("We already have a student with that e-mail address.  Try again.")
    newStudent = Student(lastName, firstName, email)
    session.add(newStudent)


def select_student_id(sess: Session) -> Student:
    """
    Prompt the user for a specific student by the student ID.  Generally
    this is not a terribly useful approach, but I have it here for
    an example.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    ID: int = -1
    while not found:
        ID = int(input("Enter the student ID--> "))
        id_count: int = sess.query(Student).filter(Student.studentId == ID).count()
        found = id_count == 1
        if not found:
            print("No student with that ID.  Try again.")
    return_student: Student = sess.query(Student).filter(Student.studentId == ID).first()
    return return_student


def select_student_first_and_last_name(sess: Session) -> Student:
    """
    Select a student by the combination of the first and last name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    lastName: str = ''
    firstName: str = ''
    while not found:
        lastName = input("Student last name to delete--> ")
        firstName = input("Student first name to delete--> ")
        name_count: int = sess.query(Student).filter(Student.lastName == lastName,
                                                     Student.firstName == firstName).count()
        found = name_count == 1
        if not found:
            print("No student by that name.  Try again.")
    oldStudent = sess.query(Student).filter(Student.lastName == lastName,
                                            Student.firstName == firstName).first()
    return oldStudent


def select_student_email(sess: Session) -> Student:
    """
    Select a student by the e-mail address.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    email: str = ''
    while not found:
        email = input("Enter the student ID--> ")
        id_count: int = sess.query(Student).filter(Student.eMail == email).count()
        found = id_count == 1
        if not found:
            print("No student with that email address.  Try again.")
    return_student: Student = sess.query(Student).filter(Student.eMail == email).first()
    return return_student

def delete_student(session: Session):
    """
    Prompt the user for a student to delete and delete them.
    :param session:     The current connection to the database.
    :return:            None
    """
    student: Student = select_student(session)
    recs = sess.query(Student).join(Enrollment, Student.studentId == Enrollment.studentId).join(
        Section, Enrollment.sectionId == Section.sectionId).filter(
        Student.studentId == student.studentId).add_columns(
        Student.lastName, Student.firstName, Section.courseNumber, Section.sectionNumber).all()
    student_enrollments: int = sess.query(Student).join(Enrollment, Student.studentId == Enrollment.studentId).filter(
        Student.studentId == Enrollment.studentId).count()
    if student_enrollments > 0:
        print(f"Student has the following sections so they will not be deleted")
        for stu in recs:
            print(f"Student name: {stu.lastName}, {stu.firstName}, Course Number: {stu.courseNumber},"
                  f" Section: {stu.sectionNumber}")
    else:
        session.delete(student)

def list_student(session: Session):
    """
    List all of the students, sorted by the last name first, then the first name.
    :param session:
    :return:
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    students: [Student] = list(session.query(Student).order_by(Student.lastName, Student.firstName))
    for student in students:
        print(student)

def select_student_from_list(session):
    """
    This is just a cute little use of the Menu object.  Basically, I create a
    menu on the fly from data selected from the database, and then use the
    menu_prompt method on Menu to display characteristic descriptive data, with
    an index printed out with each entry, and prompt the user until they select
    one of the Students.
    :param session:     The connection to the database.
    :return:            None
    """
    # query returns an iterator of Student objects, I want to put those into a list.  Technically,
    # that was not necessary, I could have just iterated through the query output directly.
    students: [Department] = list(sess.query(Department).order_by(Department.lastName, Department.firstName))
    options: [Option] = []  # The list of menu options that we're constructing.
    for student in students:
        # Each time we construct an Option instance, we put the full name of the student into
        # the "prompt" and then the student ID (albeit as a string) in as the "action".
        options.append(Option(student.lastName + ', ' + student.firstName, student.studentId))
    temp_menu = Menu('Student list', 'Select a student from this list', options)
    # text_studentId is the "action" corresponding to the student that the user selected.
    text_studentId: str = temp_menu.menu_prompt()
    # get that student by selecting based on the int version of the student id corresponding
    # to the student that the user selected.
    returned_student = sess.query(Department).filter(Department.studentId == int(text_studentId)).first()
    # this is really just to prove the point.  Ideally, we would return the student, but that
    # will present challenges in the exec call, so I didn't bother.
    print("Selected student: ", returned_student)

def select_student(session):
    """
    Select a student by the combination of the last and first.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    last_name: str = ''
    first_name: str = ''
    while not found:
        last_name = input("Student's last name--> ")
        first_name = input("Student's first name--> ")
        name_count: int = sess.query(Student).filter(Student.lastName == last_name,
                                                     Student.firstName == first_name).count()
        found = name_count == 1
        if not found:
            print("No student found by that name.  Try again.")
    student: Student = sess.query(Student).filter(Student.lastName == last_name,
                                                  Student.firstName == first_name).first()
    return student

def add_department(session: Session):
    """
    Prompt the user for the information for a new student and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    unique_department: bool = False
    unique_abbreviation: bool = False
    unique_chair_name: bool = False
    unique_office: bool = False
    unique_description: bool = False
    department_name: str = ''
    abbreviation: str = ''
    chair_name: str = ''
    building: str = ''
    office: int = -1
    description: str = ''
    # Note that there is no physical way for us to duplicate the student_id since we are
    # using the Identity "type" for studentId and allowing PostgreSQL to handle that.
    # See more at: https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-identity-column/
    while not unique_abbreviation or not unique_chair_name or not unique_office or not unique_description:
        department_name = input("Department name--> ")
        abbreviation = input("Abbreviation--> ")
        chair_name = input("Chair name--> ")
        building = input("Building name--> ")
        office = int(input("Office number--> "))
        description = input("Description--> ")

        department_count: int = session.query(Department).filter(Department.departmentName == department_name).count()
        unique_department = department_count == 0
        if not unique_department:
            print("We already have a department by that name.  Try again.")
        if unique_department:
            abbreviation_count: int = session.query(Department).filter(Department.abbreviation == abbreviation).count()
            unique_abbreviation = abbreviation_count == 0
            if not unique_abbreviation:
                print("We already have a abbreviation by that name.  Try again.")
            if unique_abbreviation:
                chair_count = session.query(Department).filter(Department.chairName == chair_name).count()
                unique_chair_name = chair_count == 0
                if not unique_chair_name:
                    print("We already have a department with that professor.  Try again.")
                if unique_chair_name:
                    office_count: int = session.query(Department).filter(Department.building == building,
                                                                Department.office == office).count()
                    unique_office = office_count == 0
                    if not unique_office:
                        print("That office currently already is occupied.  Try again.")
                    if unique_office:
                        description_count: int = session.query(Department).filter(
                            Department.description == description).count()
                        unique_description = description_count == 0
                        if not unique_description:
                            print("We already have that description.  Try again.")

    newDepartment = Department(department_name, abbreviation, chair_name, building, office, description)
    session.add(newDepartment)

def delete_department(session: Session):
    """
    Prompt the user for a student by the last name and first name and delete that
    student.
    :param session: The connection to the database.
    :return:        None
    """
    print("deleting a department")
    OldDepartment = select_department_from_list(session)
    n_courses = session.query(Course).filter(Course.departmentAbbreviation == OldDepartment.abbreviation).count()
    if n_courses > 0:
        print(f"Sorry, there are {n_courses} courses in that department.  Delete them first, "
              "then come back here to delete the department.")
    else:
        session.delete(OldDepartment)


def list_department(session: Session):
    """
    List all of the students, sorted by the last name first, then the first name.
    :param session:
    :return:
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    departments: [Department] = list(session.query(Department).order_by(Department.abbreviation))
    for department in departments:
        print(department)


def select_department_from_list(session: Session):
    """
    This is just a cute little use of the Menu object.  Basically, I create a
    menu on the fly from data selected from the database, and then use the
    menu_prompt method on Menu to display characteristic descriptive data, with
    an index printed out with each entry, and prompt the user until they select
    one of the Students.
    :param session:     The connection to the database.
    :return:            None
    """
    # query returns an iterator of Student objects, I want to put those into a list.  Technically,
    # that was not necessary, I could have just iterated through the query output directly.
    departments: [Department] = list(session.query(Department).order_by(Department.department_name))
    options: [Option] = []                      # The list of menu options that we're constructing.
    for department in departments:
        # Each time we construct an Option instance, we put the full name of the student into
        # the "prompt" and then the student ID (albeit as a string) in as the "action".
        options.append(Option(department.department_name, department.department_name))
    temp_menu = Menu('Department list', 'Select a department from this list', options)
    # text_studentId is the "action" corresponding to the student that the user selected.
    text_department_name: str = temp_menu.menu_prompt()
    # get that student by selecting based on the int version of the student id corresponding
    # to the student that the user selected.
    selected_department = session.query(Department).filter(Department.department_name == str(text_department_name)).first()
    # this is really just to prove the point.  Ideally, we would return the student, but that
    # will present challenges in the exec call, so I didn't bother.
    print("Selected department: ", selected_department)
    return selected_department

def select_department(sess: Session) -> Department:
    """
    Prompt the user for a specific department by the department abbreviation.
    :param sess:    The connection to the database.
    :return:        The selected department.
    """
    found: bool = False
    abbreviation: str = ''
    while not found:
        abbreviation = input("Enter the department abbreviation--> ")
        abbreviation_count: int = sess.query(Department). \
            filter(Department.abbreviation == abbreviation).count()
        found = abbreviation_count == 1
        if not found:
            print("No department with that abbreviation.  Try again.")
    return_department: Department = sess.query(Department). \
        filter(Department.abbreviation == abbreviation).first()
    return return_department

def add_course(session: Session):
    """
    Prompt the user for the information for a new course and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    print("Which department offers this course?")
    department: Department = select_department(sess)
    unique_number: bool = False
    unique_name: bool = False
    number: int = -1
    name: str = ''
    while not unique_number or not unique_name:
        name = input("Course full name--> ")
        number = int(input("Course number--> "))
        name_count: int = session.query(Course).filter(Course.departmentAbbreviation == department.abbreviation,
                                                       Course.name == name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a course by that name in that department.  Try again.")
        if unique_name:
            number_count = session.query(Course). \
                filter(Course.departmentAbbreviation == department.abbreviation,
                       Course.courseNumber == number).count()
            unique_number = number_count == 0
            if not unique_number:
                print("We already have a course in this department with that number.  Try again.")
    description: str = input('Please enter the course description-->')
    units: int = int(input('How many units for this course-->'))
    course = Course(department, number, name, description, units)
    session.add(course)

def select_course(sess: Session) -> Course:
    """
    Select a course by the combination of the department abbreviation and course number.
    Note, a similar query would be to select the course on the basis of the department
    abbreviation and the course name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    department_abbreviation: str = ''
    course_number: int = -1
    while not found:
        department_abbreviation = input("Department abbreviation--> ")
        course_number = int(input("Course Number--> "))
        name_count: int = sess.query(Course).filter(Course.departmentAbbreviation == department_abbreviation,
                                                    Course.courseNumber == course_number).count()
        found = name_count == 1
        if not found:
            print("No course by that number in that department.  Try again.")
    course = sess.query(Course).filter(Course.departmentAbbreviation == department_abbreviation,
                                       Course.courseNumber == course_number).first()
    return course

def list_course(sess: Session):
    """
    List all courses currently in the database.
    :param sess:    The connection to the database.
    :return:        None
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    courses: [Course] = list(sess.query(Course).order_by(Course.courseNumber))
    for course in courses:
        print(course)

def move_course_to_new_department(sess: Session):
    """
    Take an existing course and move it to an existing department.  The course has to
    have a department when the course is created, so this routine just moves it from
    one department to another.

    The change in department has to occur from the Course end of the association because
    the association is mandatory.  We cannot have the course not have any department for
    any time the way that we would if we moved it to a new department from the department
    end.

    Also, the change in department requires that we make sure that the course will not
    conflict with any existing courses in the new department by name or number.
    :param sess:    The connection to the database.
    :return:        None
    """
    print("Input the course to move to a new department.")
    course = select_course(sess)
    old_department = course.department
    print("Input the department to move that course to.")
    new_department = select_department(sess)
    if new_department == old_department:
        print("Error, you're not moving to a different department.")
    else:
        # check to be sure that we are not violating the {departmentAbbreviation, name} UK.
        name_count: int = sess.query(Course).filter(Course.departmentAbbreviation == new_department.abbreviation,
                                                    Course.name == course.name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a course by that name in that department.  Try again.")
        if unique_name:
            # Make sure that moving the course will not violate the {departmentAbbreviation,
            # course number} uniqueness constraint.
            number_count = sess.query(Course).filter(Course.departmentAbbreviation == new_department.abbreviation,
                       Course.courseNumber == course.courseNumber).count()
            if number_count != 0:
                print("We already have a course by that number in that department.  Try again.")
            else:
                course.set_department(new_department)

def list_department_course(sess: Session):
    department = select_department(sess)
    dept_courses: [Course] = department.get_courses()
    print("Course for department: " + str(department))
    for dept_course in dept_courses:
        print(dept_course)

def delete_course(sess: Session):
    print("Deleting a course")
    found: bool = False
    while not found:
        OldCourse = select_course(sess)

        section_count = sess.query(Section).filter(Section.courseNumber == OldCourse.courseNumber).count()

        if section_count > 0:
            print("Cannot delete the course because it has associated sections.")
        else:
            found = 1

    sess.delete(OldCourse)
    print("Course deleted.")

def add_section(sess: Session):
    print("Adding a new section")
    course = select_course(sess)

    unique_year: bool = False
    unique_semester: bool = False
    unique_schedule: bool = False
    unique_startTime: bool = False
    unique_building: bool = False
    unique_room: bool = False
    unique_instructor: bool = False

    section_number: int = -1
    year: int = -1
    semester: str = ''
    schedule: str = ''
    startTime: time
    building: str = ''
    room: int = -1
    instructor: str = ''

    while not (unique_year and unique_semester and unique_schedule and unique_startTime and unique_building and
                unique_room) or (unique_year and unique_semester and unique_schedule and unique_startTime
                                 and unique_instructor):
        section_number = int(input("Section number--> "))
        year = int(input("Section Year--> "))
        semester = input("Semester--> ")
        schedule = input("Schedule--> ")
        start_hour = int(input("Start hour--> "))
        start_minute = int(input("Start minute--> "))
        startTime = time(start_hour, start_minute)
        building = input("Building--> ")
        room = int(input("Room--> "))
        instructor = input("Instructor--> ")

        section_count = sess.query(Section).filter(Section.courseNumber == course.courseNumber,
            Section.sectionNumber == section_number).count()

        unique_number = section_count == 0

        if not unique_number:
            print("A section with that number already exists for this course. Try again.")
        if unique_number:
            key1_count = sess.query(Section).filter(Section.sectionYear == year, Section.semester == semester,
                                                    Section.schedule == schedule, Section.startTime == startTime,
                                                    Section.building == building, Section.room == room).count()
            unique_year = unique_semester = unique_schedule = unique_startTime = unique_building = \
                unique_room = key1_count == 0
            if not unique_year:
                print("That room in that building is already booked at that time.  Try again.")
        if unique_number:
            key2_count = sess.query(Section).filter(Section.sectionYear == year, Section.semester == semester,
                                                    Section.schedule == schedule, Section.startTime == startTime,
                                                    Section.instructor == instructor).count()
            unique_year = unique_semester = unique_schedule = unique_startTime = unique_building = \
                unique_room = key2_count == 0
            if not unique_year:
                print("That instructor is already booked at that time and schedule.  Try again.")

    new_section = Section(course, section_number, semester, year, building, room, schedule, startTime,
                          instructor)
    sess.add(new_section)
    print("Section added successfully.")

def list_section_course(sess):
    sections: [Section] = list(sess.query(Section).order_by(Section.sectionNumber))
    for section in sections:
        print(section)

def select_section(sess: Session) -> Section:
    found: bool = False
    department_abbreviation: str = ''
    course_number: int = -1
    section_number: int = -1
    while not found:
        department_abbreviation = input("Department abbreviation--> ")
        course_number = int(input("Course Number--> "))
        section_number = int(input("Section Number--> "))
        name_count: int = sess.query(Section).filter(Section.departmentAbbreviation == department_abbreviation,
                                                    Section.courseNumber == course_number,
                                                     Section.sectionNumber == section_number).count()
        found = name_count == 1
        if not found:
            print("No section by that number in that course.  Try again.")
    section = sess.query(Section).filter(Section.departmentAbbreviation == department_abbreviation,
                                       Section.courseNumber == course_number,
                                         Section.sectionNumber == section_number).first()
    return section

def delete_section(sess: Session):
    print("Deleting a section")
    section: Section = select_section(sess)
    recs = sess.query(Section).join(Enrollment, Enrollment.sectionId == Section.sectionId).join(
        Student, Enrollment.studentId == Student.studentId).filter(
        Section.sectionId == section.sectionId).add_columns(
        Student.lastName, Student.firstName, Section.courseNumber, Section.sectionNumber).all()
    section_enrollments: int = sess.query(Section).join(Enrollment, Section.sectionId == Enrollment.sectionId).filter(
        Section.sectionId == Enrollment.sectionId).count()
    if section_enrollments > 0:
        print(f"Section has the following students so it will not be deleted")
        for stu in recs:
            print(f"Student name: {stu.lastName}, {stu.firstName}, Course Number: {stu.courseNumber},"
                  f" Section: {stu.sectionNumber}")
    else:
        sess.delete(section)

def add_major(session: Session):
    """
    Prompt the user for the information for a new major and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    print("Which department offers this major?")
    department: Department = select_department(sess)
    unique_name: bool = False
    name: str = ''
    while not unique_name:
        name = input("Major name--> ")
        name_count: int = session.query(Major).filter(Major.departmentAbbreviation == department.abbreviation,
                                                      ).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a major by that name in that department.  Try again.")
    description: str = input('Please give this major a description -->')
    major: Major = Major(department, name, description)
    session.add(major)
    session.flush()

def add_student_major(sess):
    unique_student_major: bool = False
    while not unique_student_major:
        student = select_student(sess)
        major = select_major(sess)
        student_major_count: int = sess.query(StudentMajor).filter(StudentMajor.studentId == student.studentID,
                                                                   StudentMajor.majorName == major.name).count()
        unique_student_major = student_major_count == 0
        if not unique_student_major:
            print("That student already has that major.  Try again.")
    student.add_major(major)
    """The student object instance is mapped to a specific row in the Student table.  But adding
    the new major to its list of majors does not add the new StudentMajor instance to this session.
    That StudentMajor instance was created and added to the Student's majors list inside of the
    add_major method, but we don't have easy access to it from here.  And I don't want to have to 
    pass sess to the add_major method.  So instead, I add the student to the session.  You would
    think that would cause an insert, but SQLAlchemy is smart enough to know that this student 
    has already been inserted, so the add method takes this to be an update instead, and adds
    the new instance of StudentMajor to the session.  THEN, when we flush the session, that 
    transient instance of StudentMajor gets inserted into the database, and is ready to be 
    committed later (which happens automatically when we exit the application)."""
    sess.add(student)                           # add the StudentMajor to the session
    sess.flush()

def add_major_student(sess):
    major: Major = select_major(sess)
    student: Student = select_student(sess)
    student_major_count: int = sess.query(StudentMajor).filter(StudentMajor.studentId == student.studentId,
                                                               StudentMajor.majorName == major.name).count()
    unique_student_major: bool = student_major_count == 0
    while not unique_student_major:
        print("That major already has that student.  Try again.")
        major = select_major(sess)
        student = select_student(sess)
    major.add_student(student)
    """The major object instance is mapped to a specific row in the Major table.  But adding
    the new student to its list of students does not add the new StudentMajor instance to this session.
    That StudentMajor instance was created and added to the Major's students list inside of the
    add_student method, but we don't have easy access to it from here.  And I don't want to have to 
    pass sess to the add_student method.  So instead, I add the major to the session.  You would
    think that would cause an insert, but SQLAlchemy is smart enough to know that this major 
    has already been inserted, so the add method takes this to be an update instead, and adds
    the new instance of StudentMajor to the session.  THEN, when we flush the session, that 
    transient instance of StudentMajor gets inserted into the database, and is ready to be 
    committed later (which happens automatically when we exit the application)."""
    sess.add(major)                           # add the StudentMajor to the session
    sess.flush()

def select_major(sess) -> Major:
    """
    Select a major by its name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    name: str = ''
    while not found:
        name = input("Major's name--> ")
        name_count: int = sess.query(Major).filter(Major.name == name).count()
        found = name_count == 1
        if not found:
            print("No major found by that name.  Try again.")
    major: Major = sess.query(Major).filter(Major.name == name).first()
    return major

def delete_student_major(sess):
    """Undeclare a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the student and the major that they no longer have.")
    student: Student = select_student(sess)
    major: Major = select_major(sess)
    student.remove_major(major)

def delete_major_student(sess):
    """Remove a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the major and the student who no longer has that major.")
    major: Major = select_major(sess)
    student: Student = select_student(sess)
    major.remove_student(student)

def list_major(sess: Session):
    """
    List all majors in the database.
    :param sess:    The current connection to the database.
    :return:
    """
    majors: [Major] = list(sess.query(Major).order_by(Major.departmentAbbreviation))
    for major in majors:
        print(major)

def list_student_major(sess: Session):
    """Prompt the user for the student, and then list the majors that the student has declared.
    :param sess:    The connection to the database
    :return:        None
    """
    student: Student = select_student(sess)
    recs = sess.query(Student).join(StudentMajor, Student.studentId == StudentMajor.studentId).join(
        Major, StudentMajor.majorName == Major.name).filter(
        Student.studentId == student.studentId).add_columns(
        Student.lastName, Student.firstName, Major.description, Major.name).all()
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Major: {stu.name}, Description: {stu.description}")

def list_major_student(sess: Session):
    """Prompt the user for the major, then list the students who have that major declared.
    :param sess:    The connection to the database.
    :return:        None
    """
    major: Major = select_major(sess)
    recs = sess.query(Major).join(StudentMajor, StudentMajor.majorName == Major.name).join(
        Student, StudentMajor.studentId == Student.studentId).filter(
        Major.name == major.name).add_columns(
        Student.lastName, Student.firstName, Major.description, Major.name).all()
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Major: {stu.name}, Description: {stu.description}")

def add_student_section(sess):
    unique_student_section: bool = False
    while not unique_student_section:
        student = select_student(sess)
        section = select_section(sess)
        pk_count: int = count_student_section(sess, student, section)
        unique_student_section = pk_count == 0
        if not unique_student_section:
            print("That section already has that student enrolled in it.  Try again.")
    student.add_section(section)
    sess.add(student)                           # add the StudentMajor to the session
    sess.flush()

def add_section_student(sess):
    section: Section = select_section(sess)
    student: Student = select_student(sess)
    student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentId,
                                                               Enrollment.sectionId == section.sectionId).count()
    unique_student_section: bool = student_section_count == 0
    while not unique_student_section:
        print("That section already has that student.  Try again.")
        section = select_section(sess)
        student = select_student(sess)
    section.add_student(student)
    sess.add(section)                           # add the StudentMajor to the session
    sess.flush()

def unenroll_student_section(sess):
    """Undeclare a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the student and the section that they no longer have.")
    student: Student = select_student(sess)
    section: Section = select_section(sess)
    student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentId,
                                                               Enrollment.sectionId == section.sectionId).count()
    unique_student_section: bool = student_section_count == 1
    while not unique_student_section:
        print("That student does not have that section.  Try again.")
        student = select_student(sess)
        section = select_section(sess)
        student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentId,
                                                                   Enrollment.sectionId == section.sectionId).count()
        unique_student_section = student_section_count == 1
    student.remove_enrollment(section)

def unenroll_section_student(sess):
    """Remove a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the section and the student who no longer has that section.")
    section: Section = select_section(sess)
    student: Student = select_student(sess)
    student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentId,
                                                               Enrollment.sectionId == section.sectionId).count()
    unique_student_section: bool = student_section_count == 1
    while not unique_student_section:
        print("That section does not have that student.  Try again.")
        section = select_section(sess)
        student = select_student(sess)
        student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentId,
                                                                   Enrollment.sectionId == section.sectionId).count()
        unique_student_section = student_section_count == 1
    section.remove_enrollment(student)

def list_student_section(sess: Session):
    """Prompt the user for the student, and then list the section that the student has declared.
    :param sess:    The connection to the database
    :return:        None
    """
    student: Student = select_student(sess)
    recs = sess.query(Student).join(Enrollment, Student.studentId == Enrollment.studentId).join(
        Section, Enrollment.sectionId == Section.sectionId).filter(
        Student.studentId == student.studentId).add_columns(
        Student.lastName, Student.firstName, Section.courseNumber, Section.sectionNumber).all()
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Course Number: {stu.courseNumber},"
              f" Section: {stu.sectionNumber}")

def list_section_student(sess: Session):
    """Prompt the user for the major, then list the students who have that major declared.
    :param sess:    The connection to the database.
    :return:        None
    """
    section: Section = select_section(sess)
    recs = sess.query(Section).join(Enrollment, Enrollment.sectionId == Section.sectionId).join(
        Student, Enrollment.studentId == Student.studentId).filter(
        Section.sectionId == section.sectionId).add_columns(
        Student.lastName, Student.firstName, Section.courseNumber, Section.sectionNumber).all()
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Course Number: {stu.courseNumber},"
              f" Section: {stu.sectionNumber}")

def count_student_section(sess, student: Student, section: Section):
    """Count the number of Enrollment instances for a given student & section.
    :param  sess        The current session.
    :param  student     The enrolling student.
    :param  section     The section that we want to see whether that student is enrolled."""
    pk_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentId,
        Enrollment.sectionId == section.sectionId).count()
    return pk_count

def list_enrollment(sess: Session):
    """
    List out all enrollment records sorted by department, course,
    section number.
    :param sess:    The current connection.
    :return:        None
    """
    recs = sess.query(Enrollment).order_by(Enrollment.departmentAbbreviation,
                                           Enrollment.courseNumber,
                                           Enrollment.sectionYear).all()
    for rec in recs:
        print(rec)

def add_student_PassFail(sess):
    """
    Add a student to a section as a pass/fail.
    :param sess: The current database connection.
    :return:    None
    """
    student: Student
    section: Section
    unique_student_section: bool = False
    while not unique_student_section:
        student = select_student(sess)
        section = select_section(sess)
        pk_count: int = count_student_section(sess, student, section)
        unique_student_section = pk_count == 0
        if not unique_student_section:
            print("That section already has that student enrolled in it.  Try again.")
    pass_fail = PassFail(section, student, datetime.now())
    sess.add(pass_fail)
    sess.flush()

def add_student_LetterGrade(sess):
    """
    Add a student to a section as a letter grade.
    :param sess: The current database connection.
    :return:    None
    """
    student: Student
    section: Section
    unique_student_section: bool = False
    while not unique_student_section:
        student = select_student(sess)
        section = select_section(sess)
        pk_count: int = count_student_section(sess, student, section)
        unique_student_section = pk_count == 0
        if not unique_student_section:
            print("That section already has that student enrolled in it.  Try again.")
    grade = "A"
    letter_grade = LetterGrade(section, student, grade)
    sess.add(letter_grade)
    sess.flush()

def boilerplate(sess):
    """
    Add boilerplate data initially to jump start the testing.  Remember that there is no
    checking of this data, so only run this option once from the console, or you will
    get a uniqueness constraint violation from the database.
    :param sess:    The session that's open.
    :return:        None
    """
    department: Department = Department('Computer Engineering Computer Science', 'CECS', 'Brown', 'ECS', '1', 'Yes')
    major1: Major = Major(department, 'Computer Science', 'Fun with blinking lights')
    major2: Major = Major(department, 'Computer Engineering', 'Much closer to the silicon')
    student1: Student = Student('Brown', 'David', 'david.brown@gmail.com')
    student2: Student = Student('Brown', 'Mary', 'marydenni.brown@gmail.com')
    student3: Student = Student('Disposable', 'Bandit', 'disposable.bandit@gmail.com')
    student1.add_major(major1)
    student2.add_major(major1)
    student2.add_major(major2)
    course1: Course = Course(department, 323, "Database Design Fundamentals",
                             "Basics of database design", 3)
    course2: Course = Course(department, 174, "Intro to Programming",
                             "First real programming course", 3)
    section1: Section = Section(course1, 1, 'Fall', 2023, 'ECS', 416, 'MW', time(8, 0, 0), 'Brown')
    sess.add(department)
    sess.add(course1)
    sess.add(course2)
    sess.add(major1)
    sess.add(major2)
    sess.add(student1)
    sess.add(student2)
    sess.add(student3)
    sess.add(section1)
    sess.flush()

def session_rollback(sess):
    """
    Give the user a chance to roll back to the most recent commit point.
    :param sess:    The connection to the database.
    :return:        None
    """
    confirm_menu = Menu('main', 'Please select one of the following options:', [
        Option("Yes, I really want to roll back this session", "sess.rollback()"),
        Option("No, I hit this option by mistake", "pass")
    ])
    exec(confirm_menu.menu_prompt())

if __name__ == '__main__':
    print('Starting off')
    logging.basicConfig()
    # use the logging factory to create our first logger.
    # for more logging messages, set the level to logging.DEBUG.
    # logging_action will be the text string name of the logging level, for instance 'logging.INFO'
    logging_action = debug_select.menu_prompt()
    # eval will return the integer value of whichever logging level variable name the user selected.
    logging.getLogger("sqlalchemy.engine").setLevel(eval(logging_action))
    # use the logging factory to create our second logger.
    # for more logging messages, set the level to logging.DEBUG.
    logging.getLogger("sqlalchemy.pool").setLevel(eval(logging_action))

    metadata.drop_all(bind=engine)  # start with a clean slate while in development

    # Create whatever tables are called for by our "Entity" classes.
    metadata.create_all(bind=engine)

    with Session() as sess:
        main_action: str = ''
        while main_action != menu_main.last_action():
            main_action = menu_main.menu_prompt()
            print('next action: ', main_action)
            exec(main_action)
        sess.commit()
    print('Ending normally')