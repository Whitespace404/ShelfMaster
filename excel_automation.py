import openpyxl


def read_file_and_get_details():
    wb = openpyxl.load_workbook("master_1.xlsx")
    sheet = wb["Accession Details"]

    result_dict = []
    for row in sheet.iter_rows(min_row=3, values_only=True):
        a = dict()
        a["accession_number"] = row[0]
        a["author"] = row[3]
        a["title"] = row[4]
        a["call_number"] = row[5]
        a["publisher"] = row[6]
        a["place_of_publication"] = row[7]
        a["isbn"] = row[8]
        a["vendor"] = row[9]
        a["bill_number"] = row[10]
        a["price"] = row[12]
        result_dict.append(a)

    return result_dict


def read_namelist_and_get_details():
    wb = openpyxl.load_workbook("master.xlsx")
    sheet = wb["Issue Details"]

    result_list = []
    for row in sheet.iter_rows(min_row=3, values_only=True):
        result_list.append((row[1], row[2]))

    return result_list
