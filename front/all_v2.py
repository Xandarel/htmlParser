import pandas as pd
from tqdm import tqdm
from DB_api import db

header = ['Наименование', 'Регион', 'сайт контрагента', 'НИС', 'Стандарт', 'Диаметр', 'Стенка', 'Сталь',
          'Тип длины', 'МРЦ', 'Цена наш сайт', 'Цена контрагента', 'Отклонение сайт\сайт',
          'Отклонение МРЦ/сайт', 'Демпинг сайт\сайт', 'Демпинг МРЦ', 'МРЦ ГОСТ', 'МРЦ сталь', 'МРЦ диаметр', 'МРЦ стенка']
df = pd.DataFrame(columns=header)
iterator = 0

carbon = db.select('name', 'carbon_steel', mode=0)
carbon = [i[0] for i in carbon]
columns = 'company_price.name, company_id, standard, steel, wall, diameter, city_id, ' \
          'price_min, article_id, city.name as region, company.name as company_name, url'
company_price = db.select(columns, 'company_price, city, company', 'WHERE city_id = city.id AND company_id = company.id', mod='DISTINCT', mode=0)

for cp in tqdm(company_price):
    where_min_value = "WHERE "
    where_chelpipe = "WHERE "
    if cp[2]:
        if '/' in cp[2]:
            standard = cp[2].split('/')
            if 'с тех. протоколом' in standard[-1]:
                where_min_value += f"standard like '{standard[0].strip()}%' AND "
                where_chelpipe += f"standard like '{standard[0].strip()}%' AND "
            else:
                where_min_value += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[1].strip()}%') AND "
                where_chelpipe += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[1].strip()}%') AND "
        elif cp[2] == '-':
            pass
        elif '-' in cp[2] and 'ТУ' not in cp[2]:
            standard = cp[2].split('-')[0]
            where_min_value += f"standard like '{standard.strip()}%' AND "
        elif ',' in cp[2]:
            standard = cp[2].split(',')
            where_min_value += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[1].strip()}%') AND "
            where_chelpipe += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[1].strip()}%') AND "
        else:
            where_min_value += f"standard like '{cp[2].strip()}%' AND "
            where_chelpipe += f"standard like '{cp[2].strip()}%' AND "
    if cp[3]:
        steel = cp[3].split('-')
        if steel[0] in carbon or steel[-1] in carbon:
            where_min_value += f"steel = 'угл' AND "
            # if '-' in cp[3] and cp[3] != '-':
            #     where_chelpipe += f"(steel like '{steel[0].strip()}%' OR steel like '{steel[-1].strip()}%') AND "
            # else:
            #     where_chelpipe += f"steel like '{cp[3].strip()}%' AND "
        elif '-' in cp[3] and cp[3] != '-':
            steel = cp[3].split('-')
            where_min_value += f"(steel like '{steel[0].strip()}%' OR steel like '{steel[-1].strip()}%') AND "
            where_chelpipe += f"(steel like '{steel[0].strip()}%' OR steel like '{steel[-1].strip()}%') AND "
        else:
            where_min_value += f"standard like '{cp[3].strip()}%' AND "
            where_chelpipe += f"standard like '{cp[3].strip()}%' AND "
    if cp[4]:
        where_min_value += f"wall_min <= {str(cp[4])} AND wall_max >= {str(cp[4])} AND "
        where_chelpipe += f"wall = {str(cp[4])} AND "
    if cp[5]:
        where_min_value += f"diameter_min <=  {cp[5]} AND  diameter_max >= {cp[5]} AND "
        where_chelpipe += f"diameter = {cp[5]} AND "
    if cp[6]:
        where_min_value += f"city_id = {cp[6]} AND "
        where_chelpipe += f"city_id = {cp[6]} AND "
    if cp[8]:
        where_chelpipe = f"WHERE article_id = {cp[8]} AND "

    where_min_value = ' '.join(where_min_value.split()[:-1])
    where_chelpipe = ' '.join(where_chelpipe.split()[:-1])
    # print(where_min_value)
    # print(where_chelpipe)
    min_value_columns = 'standard, diameter_min, diameter_max, steel, price, wall_min, wall_max'
    min_value = db.select(min_value_columns, 'MinValue', where_min_value)
    # print(min_value)
    chelpipe = db.select('price, type_of_length', 'chelpipe', where_chelpipe)
    # print(chelpipe)
    row = [None] * 20
    if cp[8]:
        article = db.select('article', 'articles', 'WHERE id = ?', (cp[8],))[0]
        data = [cp[0], cp[-3], cp[-1], article, cp[2], cp[5], cp[4], cp[3]]
        for i in range(len(data)):
            row[i] = data[i]
    else:
        data = [cp[0], cp[-3], cp[-1], None, cp[2], cp[5], cp[4], cp[3]]
        for i in range(len(data)):
            row[i] = data[i]

    if chelpipe:
        row[8] = chelpipe[-1]
        row[10] = chelpipe[0]
        row[12] = chelpipe[0] - cp[7]
        row[14] = chelpipe[0] > cp[7]
    else:
        row[8] = 'н/д'
        row[10] = 'н/д'
        row[12] = 'н/д'
        row[14] = 'н/д'

    if min_value:
        row[9] = min_value[-3]
        row[13] = min_value[-3] - cp[7]
        row[15] = min_value[-3] > cp[7]
        row[16] = min_value[0]
        row[17] = min_value[3]
        row[18] = str(min_value[1]) + '-' + str(min_value[2])
        row[19] = str(min_value[-2]) + '-' + str(min_value[-1])
    else:
        row[9] = 'н/д'
        row[13] = 'н/д'
        row[15] = 'н/д'
        row[16] = 'н/д'
        row[17] = 'н/д'
        row[18] = 'н/д'
        row[19] = 'н/д'

    row[11] = cp[7]

    df.loc[iterator] = row
    if iterator % 100000 == 0:
        with pd.ExcelWriter(f'savefile{iterator}.xlsx') as writer:
            df.to_excel(writer, index=False, sheet_name='Все данные')
    iterator += 1

df['сайт контрагента'] = df['сайт контрагента'] + ' '
no_ok = True
with pd.ExcelWriter('output4.xlsx') as writer:
    buf_df = pd.read_excel(writer)
    buf_df.to_excel(writer, index=False, sheet_name='Откланения по МРЦ')
    while no_ok:
        try:
            df.to_excel(writer, index=False, sheet_name='Все данные')
            no_ok = False
        except PermissionError:
            print(PermissionError)
            print('!!!Внимание!!! проблема с записью файла. исправте проблему и нажмите enter')
            a = input()



