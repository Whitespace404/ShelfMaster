import openpyxl
from shelfmaster.models import User, Entity
from shelfmaster import app, db


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
    # sheet = wb["1to4852"]
    # for row in sheet.iter_rows(min_row=2, values_only=True):
    #     details = dict()

    #     details["accession_number"] = row[1]
    #     details["author"] = convert_name(row[2])
    #     details["title"] = convert_name(row[3])
    #     details["call_number"] = row[4]
    #     details["publisher"] = row[5]
    #     details["isbn"] = row[6]
    #     details["vendor"] = row[7]
    #     details["bill_number"] = row[8]
    #     details["bill_date"] = row[9]
    #     details["price"] = row[10]
    #     details["remarks"] = row[12]
    #     details["language"] = row[13]
    #     if any(details.values()):
    #         result_dicts.append(details)

    # return result_dicts

    sheet = wb["Accession Details"]
    for row in sheet.iter_rows(min_row=3, values_only=True):
        details = dict()

        details["accession_number"] = row[0]
        details["author"] = convert_name(row[1])
        details["title"] = convert_name(row[2])
        details["call_number"] = row[3]
        details["publisher"] = row[4]
        details["isbn"] = row[5]
        details["vendor"] = row[6]
        details["bill_number"] = row[7]
        details["bill_date"] = row[8]
        details["price"] = row[9]
        details["remarks"] = row[11]
        details["language"] = row[12]
        if any(details.values()):
            result_dicts.append(details)

    return result_dicts

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
    #     details["remarks"] = row[11]
    #     details["language"] = row[12]
    #     if any(details.values()):
    #         result_dicts.append(details)

    # sheet = wb["Donated Acc. no"]
    # for row in sheet.iter_rows(min_row=308, values_only=True): # 2, then 308
    #     details = dict()

    #     details["accession_number"] = row[1]
    #     details["author"] = convert_name(row[3])
    #     details["title"] = convert_name(row[2])
    #     details["call_number"] = row[7]
    #     details["publisher"] = row[4]
    #     details["isbn"] = row[5]
    #     if row[6] is not None and row[6] != "-":
    #         details["vendor"] = "Donated by " + row[6]
    #     if any(details.values()):
    #         result_dicts.append(details)

    # return result_dicts


def read_namelist_from_upload(filename):
    workbook = openpyxl.load_workbook(filename)

    sheet = workbook["1"]
    result_dicts = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        details = dict()

        details["roll_number"] = row[0]
        details["usn"] = row[1]
        details["name"] = row[2]
        details["class_section"] = row[3]

        if all(details.values()):
            result_dicts.append(details)

    return result_dicts


def read_booklist_from_upload(filename):
    workbook = openpyxl.load_workbook(filename)

    sheet = workbook["1"]
    result_dicts = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        details = dict()
        details["accession_number"] = row[0]
        details["author"] = row[1]
        details["title"] = row[2]
        details["call_number"] = row[3]
        details["publisher"] = row[4]
        details["isbn"] = row[5]
        details["vendor"] = row[6]
        details["bill_number"] = row[7]
        details["bill_date"] = row[8]
        details["price"] = row[9]
        details["remarks"] = row[10]
        details["language"] = row[11]
        if any(details.values()):
            result_dicts.append(details)

    return result_dicts
