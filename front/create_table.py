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
min_values = db.select('*', 'MinValue', mode=0)

for min_value in tqdm(min_values):
    where = 'WHERE '

    if min_value[1]:
        where += "(standard = '' OR standard = '-' OR "
        if '-' in min_value[1]:
            standard = min_value[1].split('-')[0]
            where += f'standard LIKE \'{standard.strip()}%\') AND '
        else:
            where += f'standard LIKE \'{min_value[1].strip()}%\') AND '

    if min_value[2]:
        where += f'diameter >= {min_value[2]} AND '

    if min_values[3]:
        where += f'diameter <= {min_value[3]} AND '

    if min_value[4]:
        if '-' in min_value[4]:
            steel_min = min_value[4].split('-')[0]
            steel_max = min_value[4].split('-')[-1]
            where += f'steel >= {steel_min} AND steel <= {steel_max} AND '
        elif min_value[4] == 'угл':
            where += '( '
            for carb in carbon:
                where += f'steel like "{carb.strip()}%" OR '
            where = ' '.join(where.split()[:-1]) + ') AND '
        else:
            where += f'steel like \'{min_value[4]}%\' AND '

    if min_value[5] and min_value[6]:
        where += f"wall >= {min_value[5].replace(',', '.')} AND wall <= {min_value[6].replace(',', '.')} AND "

    if min_value[7]:
        where += f'city_id = {min_value[7]} AND '

    if min_value[-3]:
        where += f'price_min < {min_value[-3]} AND '
    where += 'article_id = articles.id AND city_id = city.id AND company_id = company.id AND '
    where = ' '.join(where.split()[:-1])
    columns = 'company_price.name, company.name as company, city.name as region, price_min, ' \
              'standard, steel, wall, diameter, url, articles.article'
    company = 'company_price, articles, city, company'

    cur = db.select(columns, company, where, mod='DISTINCT', mode=-1)
    while True:
        element = cur.fetchmany(20)

        if not element:
            break
        for d in element:
            if len(d) == 2:
                continue
            city_id = db.select('id', 'city', 'WHERE name = ?', (d[2],))[0]
            article_id = db.select('id', 'articles', 'WHERE article = ?', (d[-1],))
            chelpipe_fetch = db.select('price, type_of_length', 'chelpipe', 'WHERE article_id = ?', (article_id[0],))
            article = d[-1]
            # print(f'NIS: {d}')
            if chelpipe_fetch:
                chelpipe_price = chelpipe_fetch[0]
                type_of_length = chelpipe_fetch[1]
                df.loc[iterator] = [d[0], d[2], d[-2], article, d[4], d[-3], d[-4],
                                    d[-5], type_of_length, min_value[-3], chelpipe_price, d[3], d[3] - chelpipe_price,
                                    d[3] - min_value[-3], chelpipe_price > d[3], min_value[-3] > d[3],
                                    min_value[1], min_value[4], f'{min_value[2]}-{min_value[3]}', f'{min_value[5]}-{min_value[6]}']
            else:
                df.loc[iterator] = [d[0], d[2], d[-2], article, d[4], d[-3], d[-4],
                                    d[-5], 'н/д', min_value[-3], 'н/д', d[3], 'н/д',
                                    d[3] - min_value[-3], '', min_value[-3] > d[3],
                                    min_value[1], min_value[4], f'{min_value[2]}-{min_value[3]}', f'{min_value[5]}-{min_value[6]}']
            iterator += 1

# ---------------------------------------------------
# Выборка с article_id = None
    new_where = where.replace('article_id = articles.id', 'article_id is NULL')
    new_columns = columns.replace('articles.article', 'article_id')
    cur = db.select(new_columns, company, new_where, mod='DISTINCT', mode=-1)
    while True:
        element = cur.fetchmany(20)
        if not element:
            break

        for d in element:
            if len(d) == 2:
                continue
            city_id = db.select('id', 'city', 'WHERE name = ?', (d[2],))[0]
            chelpipe_where = 'WHERE '
            if d[4]:  # standard
                if '/' in d[4]:
                    standard = d[4].split('/')
                    chelpipe_where += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[-1].strip()}%') AND "
                else:
                    chelpipe_where += f"standard like '{d[4].strip()}%' AND "

            if d[5]:  # steel
                if '-' in d[5]:
                    steels = d[5].split('-')
                    chelpipe_where += f"(steel like '{steels[0].strip()}%' OR steel like '{steels[-1].strip()}%') AND "
                else:
                    chelpipe_where += f"steel like '{d[5].strip()}%' AND "
            if d[6]:  # wall
                chelpipe_where += f" wall = {d[6]} AND "
            if d[7]:  # diameter
                chelpipe_where += f"diameter = {d[7]} AND "
            chelpipe_where = ' '.join(chelpipe_where.split()[:-1])
            # print(chelpipe_where)
            chelpipe_fetch = db.select('price, type_of_length', 'chelpipe', chelpipe_where)
            # print(f'No NIS: {d}')
            article = d[-1]
            if chelpipe_fetch:
                chelpipe_price = chelpipe_fetch[0]
                type_of_length = chelpipe_fetch[1]
                df.loc[iterator] = [d[0], d[2], d[-2], article, d[4], d[-3], d[-4],
                                    d[-5], type_of_length, min_value[-3], chelpipe_price, d[3], d[3] - chelpipe_price,
                                    d[3] - min_value[-3], chelpipe_price > d[3], min_value[-3] > d[3],
                                    min_value[1], min_value[4], f'{min_value[2]}-{min_value[3]}', f'{min_value[5]}-{min_value[6]}']
            else:
                df.loc[iterator] = [d[0], d[2], d[-2], article, d[4], d[-3], d[-4],
                                    d[-5], 'н/д', min_value[-3], 'н/д', d[3], 'н/д',
                                    d[3] - min_value[-3], 'н/д', min_value[-3] > d[3],
                                    min_value[1], min_value[4], f'{min_value[2]}-{min_value[3]}', f'{min_value[5]}-{min_value[6]}']
            iterator += 1
df['сайт контрагента'] = df['сайт контрагента'] + ' '
with pd.ExcelWriter('Отклонения.xlsx') as writer:
    df.to_excel(writer, index=False, sheet_name='Откланения по МРЦ')
