import pandas as pd
from tqdm import tqdm
from DB_api import db

header = ['Наименование', 'Регион', 'сайт контрагента', 'НИС', 'Стандарт', 'Диаметр', 'Стенка', 'Сталь',
          'Тип длины', 'Цена наш сайт', 'Цена контрагента', 'Отклонение сайт\сайт', 'Демпинг сайт\сайт']
df = pd.DataFrame(columns=header)
iterator = 0

chelpipe = db.select('chelpipe.*, city.name as region, articles.article as article',
                     'chelpipe, city, articles',
                     'WHERE city_id = city.id AND article_id = articles.id',
                     mod='DISTINCT', mode=0)
for chlpp in tqdm(chelpipe):
    where = 'WHERE '
    if chlpp[2]:
        where += f"standard like '{chlpp[2]}%' AND "
    if chlpp[3]:
        where += f"steel like '{chlpp[3]}%' AND "
    if chlpp[4]:
        where += f"diameter = {chlpp[4]} AND "
    if chlpp[5]:
        where += f"wall = {chlpp[5]} AND "
    if chlpp[6] != 14:
        where += f"city_id = {chlpp[6]} AND "
    where += f"price_min < {chlpp[-6]} AND "
    where = ' '.join(where.split()[:-1])
    res_list = [element for element in db.select('company_price.name, price_min, url, company.name as company',
                                                 'company_price, company',
                                                 where + ' AND company_id = company.id',
                                                 mod='DISTINCT', mode=0)]
    res_list.extend(db.select('company_price.name, price_min, url, company.name as company',
                              'company_price, company',
                              'WHERE article_id = ? AND city_id = ? AND price_min < ? AND company_id = company.id',
                              (chlpp[-5], chlpp[6], chlpp[-6]),
                              mod='DISTINCT', mode=0))
    for rl in res_list:
        df.loc[iterator] = [rl[0],  # Наименование
                            chlpp[6],  # Регион
                            rl[2],  # сайт контрагента
                            chlpp[-1],  # НИС
                            chlpp[2],  # Стандарт
                            chlpp[4],  # Диаметр
                            chlpp[5],  # Стенка
                            chlpp[3],  # Сталь
                            chlpp[-4],  # Тип длины
                            chlpp[-6],  # Цена наш сайт
                            rl[1],  # Цена контрагента
                            chlpp[-6] - rl[1],  # Отклонение сайт\сайт
                            rl[1] < chlpp[-6]]  # Демпинг сайт\сайт
        iterator += 1

with pd.ExcelWriter('отклонения ЧТПЗ.xlsx') as writer:
    df.to_excel(writer, index=False, sheet_name='Отклонения по сайту')




