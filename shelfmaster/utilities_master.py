import openpyxl
from shelfmaster.models import User, Entity
from shelfmaster import app, db

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
    wb = openpyxl.load_workbook("booklist.xlsx")
    result_dicts = []
    sheet = wb["1to4852"]
    for row in sheet.iter_rows(min_row=2, values_only=True):
        details = dict()

        details["accession_number"] = row[1]
        details["author"] = convert_name(row[2])
        details["title"] = convert_name(row[3])
        details["call_number"] = row[4]
        details["publisher"] = row[5]
        details["isbn"] = row[6]
        details["vendor"] = row[7]
        details["bill_number"] = row[8]
        details["bill_date"] = row[9]
        details["price"] = row[10]
        details["place_of_publication"] = row[11]  # "location"
        details["remarks"] = row[12]
        details["language"] = row[13]
        if any(details.values()):
            result_dicts.append(details)

    return result_dicts

    # sheet = wb["4853- 14925"]
    # for row in sheet.iter_rows(min_row=3, values_only=True):
    #     details = dict()

    #     details["accession_number"] = row[0]
    #     details["author"] = convert_name(row[1])
    #     details["title"] = convert_name(row[2])
    #     details["call_number"] = row[3]
    #     details["publisher"] = row[4]
    #     details["isbn"] = row[5]
    #     details["vendor"] = row[6]
    #     details["bill_number"] = row[7]
    #     details["bill_date"] = row[8]
    #     details["price"] = row[9]
    #     details["place_of_publication"] = row[10]  # "location"
    #     details["remarks"] = row[11]
    #     details["language"] = row[12]
    #     if any(details.values()):
    #         result_dicts.append(details)

    # return result_dicts

    # sheet = wb["14926-15874"]
    # for row in sheet.iter_rows(min_row=3, values_only=True):
    #     details = dict()

    #     details["accession_number"] = row[0]
    #     details["author"] = convert_name(row[1])
    #     details["title"] = convert_name(row[2])
    #     details["call_number"] = row[3]
    #     details["publisher"] = row[4]
    #     details["isbn"] = row[5]
    #     details["vendor"] = row[6]
    #     details["bill_number"] = row[7]
    #     details["bill_date"] = row[8]
    #     details["price"] = row[9]
    #     details["place_of_publication"] = row[10]  # "location"
    #     details["remarks"] = row[11]
    #     details["language"] = row[12]
    #     if any(details.values()):
    #         result_dicts.append(details)

    # return result_dicts


def read_namelist():
    workbook = openpyxl.load_workbook("namelist.xlsx")
    results = []
    for std in range(2, 13):
        sheet = workbook[str(std)]

        blanks = 0
        current_class = None
        skip_next = False

        for row in sheet.iter_rows(min_row=1, values_only=True):  # first row ignored
            if not any(row):
                blanks += 1
                if blanks == 2:  # two blank rows indicate end of class
                    current_class = None
                continue
            else:
                blanks = 0

            if row[0] and not all(row[1:3]):  # (<class>, None, None)
                current_class = row[0]
                skip_next = True  # next will be the header
                continue
            elif skip_next:
                skip_next = False
                continue  # skips the header
            else:
                results.append([current_class, row[1], row[2]])
    return results
