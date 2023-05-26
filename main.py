import logging
from menu_definitions import menu_main, department_select, debug_select
from db_connection import engine, Session
from orm_base import metadata
# Note that until you import your SQLAlchemy declarative classes, such as Student, Python
# will not execute that code, and SQLAlchemy will be unaware of the mapped table.
from Department import Department
from Option import Option
from Menu import Menu


def add_department(session: Session):
    """
    Prompt the user for the information for a new student and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    #unique_department: bool = False
    unique_abbreviation: bool = False
    unique_chair_name: bool = False
    unique_office: bool = False
    unique_description: bool = False
    department_name: str = ''
    abbreviation: str = ''
    chair_name: str = ''
    building: str = ''
    office: int = ''
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

        abbreviation_count: int = session.query(Department).filter(Department.abbreviation == abbreviation).count()

        unique_abbreviation = abbreviation_count == 0
        if not unique_abbreviation:
            print("We already have a abbreviation by that name.  Try again.")
        if unique_abbreviation:
            chair_count = session.query(Department).filter(Department.chair_name == chair_name).count()
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
                    description_count: int = session.query(Department).filter(Department.description == description).count()
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
    print("deleting a student")
    OldDepartment = select_department_from_list(session)
    session.delete(OldDepartment)


def list_departments(session: Session):
    """
    List all of the students, sorted by the last name first, then the first name.
    :param session:
    :return:
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    departments: [Department] = list(session.query(Department).order_by(Department.department_name))
    for department in departments:
        print(department)


def select_department_from_list(session):
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