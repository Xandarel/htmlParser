import xlrd
import json


def getBGColor(book, sheet, row, col):
    xfx = sheet.cell_xf_index(row, col)
    xf = book.xf_list[xfx]
    bgx = xf.background.pattern_colour_index
    pattern_colour = book.colour_map[bgx]
    return pattern_colour


rb = xlrd.open_workbook('prajs_maksimet.xls', formatting_info=True)
product = list()
main_dict = dict()
sublist_left = list()
sublist_right = list()
dict217 = {'наименование': '',
           'Ø 4-5': 0,
           'Ø 6-6,5': 0,
           'Ø 8': 0,
           'Ø 10': 0}

sub_dict = {'Наименование, параметры': '',
            'цена до 5 тонн': 0,
            'цена от 5 тонн': 0,
            'цена за лист': 0,
            'цена за 1 кг': 0}

sheet = rb.sheet_by_index(0)
with open('maksimet.json', "w",  encoding='utf-8') as file:
    for row_num in range(sheet.nrows):
        if row_num < 12:
            continue
        elif row_num > 223:
            break
        for column in range(sheet.ncols):
            if getBGColor(rb, sheet, row_num, column) is not None:
                if sheet.cell(row_num, column).value == '':
                    continue
                if len(product) < 2:
                    product.append(sheet.cell(row_num, column).value)
                elif column < 5:  # новый товар в левой части таблицы
                    sublist_left.clear()
                    product[0] = sheet.cell(row_num, column).value
                else: # новый товар в правой части таблицы
                    sublist_right.clear()
                    product[1] = sheet.cell(row_num, column).value
            if row_num >= 216 and column < 6:
                if (column - 1) % 5 == 0:
                    if row_num == 216:
                        dict217['наименование'] = 'Выпрямление арматуры и круга из бухт          (за тонну)'
                    else:
                        dict217['наименование'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 1:
                    dict217['Ø 4-5'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 2:
                    dict217['Ø 6-6,5'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 3:
                    dict217['Ø 8'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 4:
                    dict217['Ø 10'] = sheet.cell(row_num, column).value
                continue
            else:
                if (column - 1) % 5 == 0 and column != 11:
                    sub_dict['Наименование, параметры'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 1:
                    sub_dict['цена до 5 тонн'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 2:
                    sub_dict['цена от 5 тонн'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 3:
                    sub_dict['цена за лист'] = sheet.cell(row_num, column).value
                elif (column - 1) % 5 == 4:
                    sub_dict['цена за 1 кг'] = sheet.cell(row_num, column).value

            if row_num >= 216 and column == 6:
                json_list = json.dumps({product[0]: dict217},  ensure_ascii=False).replace('}}', '}},\n')
                file.write(json_list)
                dict217.clear()
            elif column == 5 and row_num != 215:
                json_list = json.dumps({product[0]: sub_dict},  ensure_ascii=False).replace('}}', '}},\n')
                file.write(json_list)

        json_list = json.dumps({product[1]: sub_dict},  ensure_ascii=False).replace('}}', '}},\n')
        file.write(json_list)
        sublist_right.append(sub_dict)

with open('maksimet.json', "r",  encoding='utf-8') as file:
    data = file.read()
with open('maksimet.json', "w",  encoding='utf-8') as file:
    file.write(f'[{data[:-2]}]')
