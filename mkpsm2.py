import json
import xlrd
import re
from mkpsm import search_merged_element


rb = xlrd.open_workbook('Трубы профильные.xls', formatting_info=True)
sheet = rb.sheet_by_index(0)
font = rb.font_list
merged_cells = sheet.merged_cells
merged_cells.sort(key=lambda x: x[1])
#print(merged_cells)
lable = list()
main_list = list()

for row_num in range(sheet.nrows):
    if row_num < 10:
        continue
    for column in range(sheet.ncols):

        if column > 17:
            break
        if search_merged_element(row_num + 1) is not None and sheet.cell(row_num, column).value != '':
            if len(lable) < 2:
                lable.append(re.sub(' +', ' ', sheet.cell(row_num, column).value.strip()))
            elif column < 7:
                cell_xf = rb.xf_list[sheet.cell_xf_index(row_num, column)]
                if font[cell_xf.font_index].italic:
                    lable[0] = re.sub(' +', ' ', sheet.cell(row_num, column).value.strip())
            else:
                cell_xf = rb.xf_list[sheet.cell_xf_index(row_num, column)]
                if font[cell_xf.font_index].italic:
                    lable[1] = re.sub(' +', ' ', sheet.cell(row_num, column).value.strip())

        if sheet.cell(row_num, column).value == 'Типоразмер' or sheet.cell(row_num, column).value == 'Цена, руб/тн':
            continue

        if column % 4 == 0:
            standard_size1 = sheet.cell(row_num, column).value
        elif column % 4 == 1:
            standard_size2 = sheet.cell(row_num, column).value
        elif column % 4 == 2:
            standard_size3 = sheet.cell(row_num, column).value
        elif column % 4 == 3:
            price = sheet.cell(row_num, column).value
            if row_num < 73 or row_num > 90:
                if column < 8:
                    if price != '':
                        main_list.append({'product': lable[0], 'standard_size1': standard_size1,
                                          'standard_size2': standard_size2, 'standard_size3': standard_size3, 'price': price})
                else:
                    if price != '':
                        main_list.append({'product': lable[1], 'standard_size1': standard_size1,
                                          'standard_size2': standard_size2, 'standard_size3': standard_size3, 'price': price})
                price = None
                standard_size1 = None
                standard_size2 = None
                standard_size3 = None

            else:
                main_list.append({'product': lable[0], 'standard_size1': standard_size1,
                                  'standard_size2': standard_size2, 'standard_size3': standard_size3, 'price': price})
                price = None
                standard_size1 = None
                standard_size2 = None
                standard_size3 = None


json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('mkpsm2.json', "w",  encoding='utf-8') as file:
    file.write(json_list)
