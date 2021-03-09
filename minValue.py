import xlrd
import json
from tqdm import tqdm


def split_string(string, separator):
    return string.split(separator)


rb = xlrd.open_workbook('Минимальные цены продаж на ГОСТ 8732 для реализации со склада АО ТД Уралтрубосталь (взамен документа №92 от 29.12.20).xlsx')
sheet = rb.sheet_by_index(0)
main_list = list()
for row_num in tqdm(range(sheet.nrows)):
    if row_num < 9:
        continue
    if row_num > 400:
        break
    wall = None
    region = sheet.cell(row_num, 0).value
    steel_info = sheet.cell(row_num, 2).value.split(',')
    price = float(sheet.cell(row_num, 10).value.replace(' ', '').replace(',', '.'))
    # print(region)
    # print(steel_info)
    # print(price)
    # input()
    standard = steel_info[0].split('ГОСТ')[-1].strip()
    diameter = steel_info[1].strip()
    if 'угл' in diameter:
        buf = steel_info[1].strip().split()
        diameter = buf[0]
        steel = buf[1]
        wall = buf[-1]
    else:
        steel = steel_info[2].strip()
        if 'до' in steel:
            steel, wall = split_string(steel, 'до')
            wall = 'до' + wall
        elif 'свыше' in steel:
            steel, wall = split_string(steel, 'свыше')
            wall = 'свыше' + wall
        elif 'ст-ка' in steel:
            steel, wall = split_string(steel, 'ст-ка')

    if steel_info[-2] != steel_info[-1]:
        if wall is not None:
            sub_wall = steel_info[-1].split('ст-ка')[-1]
            wall += f'{sub_wall}'
        else:
            wall = steel_info[-1].split('ст-ка')[-1].strip()
    if wall == steel:
        wall = '-'
    if steel in wall:
        wall = wall.split(steel)[-1]

    try:
        diameter_min, diameter_max = map(int, diameter.split('-'))
    except ValueError:
        diameter_min = int(diameter)
        diameter_max = int(diameter)
    steel = steel.replace('ст', '').replace('.', '')
    wall = wall.replace('мм', '').replace('ст', '').strip()

    if 'до' in wall:
        try:
            wall_max = int(wall.replace('до', '').strip())
        except ValueError:
            wall_max = wall.replace('до', '').strip()

        wall_min = 0
        main_list.append({'region': region, 'standard': standard, 'diameter_min': diameter_min,
                          'diameter_max': diameter_max, 'steel': steel, 'wall_min': wall_min,
                          'wall_max': wall_max, 'price': price})
    elif 'более' in wall or 'свыше' in wall:
        try:
            wall_min = int(wall.replace('свыше', '').replace('более', '').strip())
        except ValueError:
            wall_min = wall.replace('свыше', '').replace('более', '').strip()
        wall_max = 100
        main_list.append({'region': region, 'standard': standard, 'diameter_min': diameter_min,
                          'diameter_max': diameter_max, 'steel': steel, 'wall_min': wall_min,
                          'wall_max': wall_max, 'price': price})
    elif '-' in wall:
        if wall.count('-') > 1:
            wall = wall.split()
            for w in wall:
                wall_min, wall_max = map(int, w.strip().split('-'))
                main_list.append({'region': region, 'standard': standard, 'diameter_min': diameter_min,
                                  'diameter_max': diameter_max, 'steel': steel, 'wall_min': wall_min,
                                  'wall_max': wall_max, 'price': price})
        else:
            try:
                wall_min, wall_max = map(int, wall.strip().split('-'))
            except ValueError:
                wall_min, wall_max = wall.strip().split('-')
            main_list.append({'region': region, 'standard': standard, 'diameter_min': diameter_min,
                              'diameter_max': diameter_max, 'steel': steel, 'wall_min': wall_min,
                              'wall_max': wall_max, 'price': price})
    else:
        try:
            wall_min, wall_max = map(int, wall.split())
        except ValueError:
            wall_min = int(wall)
            wall_max = int(wall)
        main_list.append({'region': region, 'standard': standard, 'diameter_min': diameter_min,
                          'diameter_max': diameter_max, 'steel': steel, 'wall_min': wall_min,
                          'wall_max': wall_max, 'price': price})
    wall = None
json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('minValue.json', "w",  encoding='utf-8') as file:
    file.write(json_list)
