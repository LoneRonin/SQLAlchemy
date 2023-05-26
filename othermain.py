import logging
from menu_definitions import menu_main, debug_select
from db_connection import engine, Session
from orm_base import metadata
# Note that until you import your SQLAlchemy declarative classes, such as Department, Python
# will not execute that code, and SQLAlchemy will be unaware of the mapped table.
from Department import Department
from Option import Option
from Menu import Menu


def add_department(session: Session):
    unique_name: bool = False
    name: str = ''
    while not unique_name:
        name = input("Department name--> ")
        name_count: int = session.query(Department).filter(Department.name == name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a department by that name.  Try again.")
    newDepartment = Department(name)
    session.add(newDepartment)


def select_department(sess: Session) -> Department:
    found: bool = False
    name: str = ''
    while not found:
        name = input("Enter the department name--> ")
        name_count: int = sess.query(Department).filter(Department.name == name).count()
        found = name_count == 1
        if not found:
            print("No department with that name.  Try again.")
    return_department: Department = sess.query(Department).filter(Department.name == name).first()
    return return_department


def delete_department(session: Session):
    print("Deleting a department")
    oldDepartment = select_department(session)
    session.delete(oldDepartment)


def list_departments(session: Session):
    departments: [Department] = list(session.query(Department).order_by(Department.name))
    for department in departments:
        print(department)


def select_department_from_list(session):
    departments: [Department] = list(sess.query(Department).order_by(Department.name))
    options: [Option] = []
    for department in departments:
        options.append(Option(department.name, department.name))
    temp_menu = Menu('Department list', 'Select a department from this list', options)
    text_departmentName: str = temp_menu.menu_prompt()
    returned_department = sess.query(Department).filter(Department.name == text_departmentName).first()
    print("Selected department: ", returned_department)


if __name__ == '__main__':
    print('Starting off')
    logging.basicConfig()
    logging_action = debug_select.menu_prompt()
    logging.getLogger("sqlalchemy.engine").setLevel(eval(logging_action))
    logging.getLogger("sqlalchemy.pool").setLevel(eval(logging_action))

    metadata.drop_all(bind=engine)

    metadata.create_all(bind=engine)

    with Session() as sess:
        main_action: str = ''
        while main_action != menu_main.last_action():
            main_action = menu_main.menu_prompt()
            print('next action: ', main_action)
            exec(main_action)
        sess.commit()
    print('Ending normally')