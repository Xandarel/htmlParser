import pandas as pd
from tqdm import tqdm
from DB_api import db


def all_table():
    header = ['Компания', 'Наименование', 'Регион', 'сайт контрагента', 'НИС', 'Стандарт', 'Диаметр', 'Стенка', 'Сталь',
              'Тип длины', 'МРЦ', 'Цена ЧТПЗ минимальная', 'Цена ЧТПЗ максимальная', 'Цена контрагента минимальная',
              'Отклонение с ЧТПЗ минимальная цена', 'Отклонение с ЧТПЗ максимальная цена',
              'Отклонение МРЦ/сайт', 'Демпинг с ЧТПЗ минимальная цена', 'Демпинг с ЧТПЗ максимальная цена',
              'Демпинг МРЦ', 'МРЦ ГОСТ', 'МРЦ сталь', 'МРЦ диаметр', 'МРЦ стенка',
              'Цена контрагента максимальная', 'Номер файла']
    df = pd.DataFrame(columns=header)
    anomaly_df = pd.DataFrame(columns=header)

    anomaly_iterator = 0
    iterator = 0

    carbon = db.select('name', 'carbon_steel', mode=0)
    carbon = [i[0] for i in carbon]
    method = db.select('*', 'production_method', mode=0)
    methods = {m[0]: m[1] for m in method}
    columns = 'company_price.name, company_id, standard, steel_id, wall, diameter, city_id, '           'price_min, article_id, city.name as region, company.name as company_name, url, price_max, method_id, file_index'
    company_price = db.select(columns, 'company_price, city, company',
                              'WHERE city_id = city.id AND company_id = company.id', mod='DISTINCT', mode=0)

    where_list = list()
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
                where_chelpipe += f"standard like '{standard.strip()}%' AND "
            elif ',' in cp[2]:
                standard = cp[2].split(',')
                where_min_value += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[1].strip()}%') AND "
                where_chelpipe += f"(standard like '{standard[0].strip()}%' OR standard like '{standard[1].strip()}%') AND "
            else:
                where_min_value += f"standard like '{cp[2].strip()}%' AND "
                where_chelpipe += f"standard like '{cp[2].strip()}%' AND "
        if cp[3]:
            steel = db.select('steel', 'steels', f'WHERE id={cp[3]}')
            carbon_bool = True
            where_chelpipe += f"steel_id = {cp[3]} AND "
            if steel:
                if steel[0].strip() in carbon:
                    where_min_value += f"steel = 'угл' AND "
                    carbon_bool = False
                else:
                    where_min_value += f"steel = '{steel[0]}%' AND "

        if cp[4]:
            if type(cp[4]) == str:
                float_wall = float(cp[4].replace(',', '.'))
            else:
                float_wall = float(cp[4])
            where_min_value += f"wall_min <= {float_wall} AND wall_max >= {float_wall} AND "
            where_chelpipe += f"wall = {float_wall} AND "
        if cp[5]:
            where_min_value += f"diameter_min <=  {cp[5]} AND  diameter_max >= {cp[5]} AND "
            where_chelpipe += f"diameter = {cp[5]} AND "
        if cp[8]:
            where_chelpipe = f"WHERE article_id = {cp[8]} AND "
        if cp[6]:
            where_min_value += f"city_id = {cp[6]} AND "
            where_chelpipe += f"(city_id = {cp[6]} or city_id = 33) AND "
        if cp[13]:
            where_chelpipe += f'method_id = {cp[13]} AND '

        where_chelpipe += 'city.id = city_id AND '

        where_min_value = ' '.join(where_min_value.split()[:-1])
        where_chelpipe = ' '.join(where_chelpipe.split()[:-1])

        min_value_columns = 'standard, diameter_min, diameter_max, steel, price, wall_min, wall_max'
        where_list.append(where_min_value)
        min_value = db.select(min_value_columns, 'MinValue', where_min_value)
        chelpipe = db.select('price_min, price_max, city.name, standard', 'chelpipe, city', where_chelpipe)

        row = [None] * 26
        if cp[8]:
            article = db.select('article', 'articles', 'WHERE id = ?', (cp[8],))[0]
            data = [cp[-5], cp[0], cp[-6], cp[-4], article, cp[2], cp[5], cp[4], steel[0] if steel else None]
            for i in range(len(data)):
                row[i] = data[i]
        else:
            data = [cp[-5], cp[0], cp[-6], cp[-4], None, cp[2], cp[5], cp[4], steel[0] if steel else None]
            for i in range(len(data)):
                row[i] = data[i]

        if chelpipe:
            row[5] = chelpipe[3] if row[5] is None and cp[8] else row[5]
            row[9] = None
            row[11] = chelpipe[0]
            row[12] = chelpipe[1]
            row[14] = cp[7] - chelpipe[0]
            row[15] = cp[12] - chelpipe[1] if cp[12] and chelpipe[1] else 'н/д'
            row[17] = chelpipe[0] > cp[7]
            row[18] = chelpipe[1] > cp[12] if cp[12] and chelpipe[1] else 'н/д'
        else:
            row[9] = 'н/д'
            row[11] = 'н/д'
            row[12] = 'н/д'
            row[14] = 'н/д'
            row[15] = 'н/д'
            row[17] = 'н/д'
            row[18] = 'н/д'

        if min_value:
            row[10] = min_value[-3]
            row[16] = cp[7] - min_value[-3]
            row[19] = min_value[-3] > cp[7]
            row[20] = min_value[0]
            row[21] = min_value[3]
            row[22] = str(min_value[1]) + '-' + str(min_value[2])
            row[23] = str(min_value[-2]) + '-' + str(min_value[-1])
        else:
            row[10] = 'н/д'
            row[16] = 'н/д'
            row[19] = 'н/д'
            row[20] = 'н/д'
            row[21] = 'н/д'
            row[22] = 'н/д'
            row[23] = 'н/д'

        row[13] = cp[7]
        row[24] = cp[12]
        row[-1] = cp[-1]
        if row[13] <= 50000 or row[13] >= 200000:
            anomaly_df.loc[anomaly_iterator] = row
            anomaly_iterator += 1
        else:
            df.loc[iterator] = row
            iterator += 1

        if iterator % 100000 == 0:
            with pd.ExcelWriter(f'savefile{iterator//100000}.xlsx', options={'strings_to_urls': False}) as writer:
                df.to_excel(writer, index=False, sheet_name='Все данные')

    mrc = df[df['Демпинг МРЦ']==True]
    chelpipe = df[(df['Демпинг с ЧТПЗ максимальная цена']==True) | (df['Демпинг с ЧТПЗ минимальная цена']==True)]

    data_doc = ['Наименование - название продукта. Получаем данный столбец из сайта конкурента.',
                'Регион - город, указанный на сайте конкурента. Получаем данный столбец из сайта конкурента.'
                'сайт контрагента - url адрес товара конкурента.',
                'НИС - получается из сравнения признаков товара конкурента (ГОСТ, диаметр, стенка, сталь) и признаков товаров, указанных на нашем сайте. Если НИС пуст - значит соответствий не найдено.',
                'Стандарт - ГОСТ товара конкурента. Берется из сайта конкурента (указан не у всех).',
                'Диаметр - диаметр товара конкурента. Берется из сайта конкурента (указан не у всех).',
                'Стенка - толщина стенки товара конкурента. Берется из сайта конкурента.',
                'Сталь - сталь товара конкурента. Берется из сайта конкурента',
                'Тип длинны - столбец формируется аналогично столбцу НИС.',
                'МРЦ - цена МРЦ. Формируется из таблицы МРЦ',
                'Цена наш сайт - цена на аналогичный товар, указанная на нашем сайте. Если в таблице 0 - значит на сайте указано "по запросу"',
                'Цена контрагента - цена на товар, указанная на сайте конкурента. Если на сайте указано несколько цен - берется наименьшая',
                'Отклонение сайт/сайт - разница между товаром контрагента и аналогичным нашим товаром(если такой находится). Рассчитывается по формуле: цена контрагента - цена наш сайт',
                'Отклонение сайт/МРЦ - разница между товаром контрагента и аналогичным МРЦ товаром(если такой находится). Рассчитывается по формуле: цена контрагента - МРЦ',
                'Демпинг сайт/сайт - столбец, показываюий, является ли цена контрагента меньше нашей цены. Столбец может принимать 3 значения:',
                '    ИСТИНА(TRUE) -цена контрагента ниже нашей',
                '    ЛОЖЬ(FALSE) - цена контрагента не ниже нашей',
                '    н/д - не с чем сравнивать',
                'Демпинг МРЦ - столбец, показываюий, является ли цена контрагента меньше цены, указанной в МРЦ. Столбец может принимать 3 значения:',
                '    ИСТИНА(TRUE) -цена контрагента ниже МРЦ',
                '    ЛОЖЬ(FALSE) - цена контрагента не ниже МРЦ',
                '    н/д - не с чем сравнивать',
                'МРЦ ГОСТ - ГОСТ, указанный в МРЦ',
                'МРЦ сталь - сталь, указанная в МРЦ.',
                'МРЦ диаметр - диамерт, указанный в МРЦ. Представлен диапазоном',
                'МРЦ стенка - стенка, указанная в МРЦ. Представлена диапазоном. Значения 0-n, где n - число аналогично значению из МРЦ "до n мм". Значения n-100, где n - число аналогично значению из МРЦ "более n мм".',
                'ЧТПЗ регион - регион, указанный на сайте ЧТПЗ. Если совпадает с полем "Регион", значит найдено полное совпадение, если не совпадает, то значит совпадение товара в этом регионе не найдено и поиск нашел товар среди всех регионов чтпз. Если "н/д, то совпадений нет"']

    doc = pd.DataFrame(columns=('Документация',))
    i = 0
    for data in tqdm(data_doc):
        doc.loc[i] = data
        i += 1

    no_ok = True
    with pd.ExcelWriter('output02-03-2021.xlsx', options={'strings_to_urls': False}) as writer:
        mrc.to_excel(writer, index=False, sheet_name='Отклонения по МРЦ')
        chelpipe.to_excel(writer, index=False, sheet_name='Отклонения по сайту')
        doc.to_excel(writer, index=False, sheet_name='Документация')
        anomaly_df.to_excel(writer, index=False, sheet_name='Аномальные данные')
        while no_ok:
            try:
                df.to_excel(writer, index=False, sheet_name='Все данные')
                no_ok = False
            except PermissionError:
                print(PermissionError)
                print('!!!Внимание!!! проблема с записью файла. исправте проблему и нажмите enter')
                a = input()
