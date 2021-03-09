import xlrd
import json
from maximet_parse import getBGColor


def search_merged_element(row_num):
    result = next((i for i, v in enumerate(merged_cells) if v[1] == row_num), None)
    return result


rb = xlrd.open_workbook('nalichiye_td_uralskaya_metallobaza_0.xls', formatting_info=True)
products_list = list()
product_dict = {'М/ст': '',
                'размер': '',
                'длинна': '',
                'склад(тн)': 0,
                'цена': 0,
                'примечание': ''}
first = True
sheet = rb.sheet_by_index(0)
merged_cells = sheet.merged_cells
merged_cells.sort(key=lambda x: x[1])

with open('ural_metal_base.json', "w",  encoding='utf-8') as file:
    for rownum in range(sheet.nrows):
        if rownum < 28:
            continue
        if rownum > 1232:
            break
        for column in range(sheet.ncols):
            if rownum < 1175:
                if column <= 1:
                    continue
            else:
                if column == 0:
                    continue

            if search_merged_element(rownum + 1) is not None:
                if getBGColor(rb, sheet, rownum, column) is None or sheet.cell(rownum, column).value == '':
                    break
                else:
                    if first:
                        key = sheet.cell(rownum, column).value.strip()
                        first = False
                    else:
                        if rownum != 1224:
                            key = sheet.cell(rownum, column).value.strip()

            if column > 8:
                json_dict = json.dumps({key: product_dict}, ensure_ascii=False).replace('}}', '}}\n')
                file.write(json_dict)
                products_list.clear()
                product_dict = {'М/ст': '',
                                'размер': '',
                                'длинна': '',
                                'склад(тн)': 0,
                                'цена': 0,
                                'примечание': ''}
                break
            elif sheet.cell(rownum, column).value != '':
                if column == 1:
                    product_dict['ГОСТ'] = sheet.cell(rownum, column).value
                if column == 2:
                    product_dict['М/ст'] = sheet.cell(rownum, column).value
                elif column == 3:
                    product_dict['размер'] = sheet.cell(rownum, column).value
                elif column == 4:
                    product_dict['длинна'] = sheet.cell(rownum, column).value
                elif column == 5:
                    product_dict['склад(тн)'] = sheet.cell(rownum, column).value
                elif column == 6:
                    product_dict['цена'] = sheet.cell(rownum, column).value
                elif column == 7:
                    print(rownum, column)
                    print(sheet.cell(rownum, column).value)
                    product_dict['примечание'] = sheet.cell(rownum, column).value
            else:
                if column == 6:
                    product_dict['цена'] = 'не указана'
