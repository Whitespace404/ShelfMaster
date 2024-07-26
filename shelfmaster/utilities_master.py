import openpyxl
from shelfmaster.models import User, Entity
from shelfmaster import app, db

# def create_database():
#     with app.app_context():
#         db.create_all()

#         admin = Admin(username="rahulreji", password="power", role_id=2)
#         db.session.add(admin)
#         db.session.commit()

#         for usn_name in read_namelist():
            # u = User(
            #     username=usn_name[0],
            #     name=usn_name[1],
            #     is_teacher=False,
            #     class_section="4A",
            # )
            # db.session.add(u)
            # db.session.commit()

        # for book_details in read_booklist():
        #     entity = Entity(
        #         type="Book",
        #         title=book_details["title"],
        #         author=book_details["author"],
        #         accession_number=book_details["accession_number"],
        #         call_number=book_details["call_number"],
        #         publisher=book_details["publisher"],
        #         place_of_publication=book_details["place_of_publication"],
        #         isbn=book_details["isbn"],
        #         vendor=book_details["vendor"],
        #         bill_number=book_details["bill_number"],
        #         amount=book_details["price"],
        #         language="English",
        #     )
        #     db.session.add(entity)
        #     db.session.commit()


def convert_name(name):
    try:
        parts = name.split(", ")
    except AttributeError:
        return name

    if len(parts) == 2:
        last_name, first_name = parts
        converted_name = f"{first_name} {last_name}"
        return converted_name
    else:
        return name


def read_booklist():
    wb = openpyxl.load_workbook("Master copy 22-23 (3).xlsx")
    sheet = wb["1to4852"]

    result_dict = []
    for row in sheet.iter_rows(min_row=1, values_only=True):
        details = dict()
        details["accession_number"] = row[0]
        name = row[2]
        details["author"] = convert_name(name)
        details["title"] = convert_name(row[3])
        details["call_number"] = row[4]
        details["publisher"] = row[5]
        details["place_of_publication"] = row[7]
        details["isbn"] = row[6]
        details["vendor"] = row[7]
        details["bill_number"] = row[8]
        details["price"] = row[10]
        if row is not None:
            result_dict.append(details)

    with app.app_context():
        for book_details in result_dict:
            entity = Entity(
                type="Book",
                title=book_details["title"],
                author=book_details["author"],
                accession_number=book_details["accession_number"],
                call_number=book_details["call_number"],
                publisher=book_details["publisher"],
                place_of_publication=book_details["place_of_publication"],
                isbn=book_details["isbn"],
                vendor=book_details["vendor"],
                bill_number=book_details["bill_number"],
                amount=book_details["price"],
                language="English",
            )
            db.session.add(entity)
            db.session.commit()

def read_namelist():
    wb = openpyxl.load_workbook("../../BOOK ISSUE 24-25 - Copy.xlsx")
    sheet = wb["9"]

    result_list = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        result_list.append((row[1], row[2], row[3]))
        if row[1] and row[2] and row[3]:
            if row[0] != "SL NO":
                with app.app_context():
                    u = User(
                            username=row[2],
                            name=row[3],
                            is_teacher=False,
                            class_section=row[1],
                        )
                    db.session.add(u)
                    db.session.commit()