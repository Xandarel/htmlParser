import json
import xlrd


def search_merged_element(row_num):
    result = next((i for i, v in enumerate(merged_cells) if v[1] == row_num), None)
    if not result:
        result = next((i for i, v in enumerate(merged_cells) if v[0] == row_num - 1), None)
    return result


rb = xlrd.open_workbook('Трубы круглого сечения.xls', formatting_info=True)
sheet = rb.sheet_by_index(0)
font = rb.font_list
merged_cells = sheet.merged_cells
merged_cells.sort(key=lambda x: x[1])

# print(merged_cells)
size = ''
price = ''
lable = list()
main_list = list()

for row_num in range(sheet.nrows):
    if row_num < 12:
        continue
    elif row_num > 167:
        break

    for column in range(sheet.ncols):
        if column > 8:
            break

        if search_merged_element(row_num + 1) is not None and sheet.cell(row_num, column).value != '':
            if len(lable) < 3:
                lable.append(sheet.cell(row_num, column).value)
            elif column < 2:
                cell_xf = rb.xf_list[sheet.cell_xf_index(row_num, column)]
                cell_xf2 = rb.xf_list[sheet.cell_xf_index(row_num + 1, column)]
                if font[cell_xf.font_index].italic:
                    if font[cell_xf2.font_index].italic:
                        lable[0] = sheet.cell(row_num, column).value.strip() + sheet.cell(row_num + 1, column).value.strip()
                    else:
                        if sheet.cell(row_num, column).value.strip() not in lable[0]:
                            lable[0] = sheet.cell(row_num, column).value.strip()
            elif column < 5:
                cell_xf = rb.xf_list[sheet.cell_xf_index(row_num, column)]
                cell_xf2 = rb.xf_list[sheet.cell_xf_index(row_num + 1, column)]
                if font[cell_xf.font_index].italic:
                    if font[cell_xf2.font_index].italic:
                        lable[1] = sheet.cell(row_num, column).value.strip() + sheet.cell(row_num + 1, column).value.strip()
                    else:
                        if sheet.cell(row_num, column).value.strip() not in lable[1]:
                            lable[1] = sheet.cell(row_num, column).value.strip()
            elif column < 8:
                cell_xf = rb.xf_list[sheet.cell_xf_index(row_num, column)]
                cell_xf2 = rb.xf_list[sheet.cell_xf_index(row_num + 1, column)]
                if font[cell_xf.font_index].italic:
                    if font[cell_xf2.font_index].italic:
                        lable[2] = sheet.cell(row_num, column).value.strip() + sheet.cell(row_num + 1, column).value.strip()
                    else:
                        if sheet.cell(row_num, column).value.strip() not in lable[2]:
                            lable[2] = sheet.cell(row_num, column).value.strip()
        if sheet.cell(row_num, column).value == 'Размер' or sheet.cell(row_num, column).value == 'Цена, руб/тн':
            continue

        switch = column % 3
        if switch == 0:
            size = sheet.cell(row_num, column).value
        elif switch == 1:
            price = sheet.cell(row_num, column).value
        else:

            if size and price:
                if row_num < 84 or row_num > 155:
                    if column == 2:
                        main_list.append({'name': lable[0], 'size': size, 'price': price})
                    elif column == 5:
                        main_list.append({'name': lable[1], 'size': size, 'price': price})
                    else:
                        main_list.append({'name': lable[2], 'size': size, 'price': price})
                else:
                    main_list.append({'name': lable[0], 'size': size, 'price': price})

            size = ''
            price = ''

json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('mkpsm.json', "w",  encoding='utf-8') as file:
    file.write(json_list)
