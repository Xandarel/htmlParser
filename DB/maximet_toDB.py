import json
import datetime
from tqdm import tqdm
from DB_api import db
import re

with open("../maksimet.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, price_max, article_id, parce_date, url'
time = datetime.datetime.now().timestamp()
company_id = db.select('id', 'company', 'WHERE name = ?', ('"Максимет" ООО',))
if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"Максимет" ООО',))
    company_id = db.cur.lastrowid

for d in tqdm(data[1:]):
    key = list(d.keys())[0]
    params = d[key]

    if 'Трубы' not in key:
        continue

    steel = re.search('ст. \d{2}', key)
    if steel:
        steel = steel.group().replace('ст. ', '').strip()
    else:
        steel = None

    standard = re.search('ГОСТ \d{4,5}-?\d{2}?', key)
    if not standard:
        new_key = key.split()
        standard = f'{new_key[-2]} {new_key[-1]}'
    else:
        standard = standard.group().replace('ГОСТ', '').strip()
    diameter_wall = re.search('\d{2,4}х[+-]?([0-9]*[,])?[0-9]+', params['Наименование, параметры'])
    if not diameter_wall:
        continue
    diameter_wall = diameter_wall.group()
    diameter = float(diameter_wall.split('х')[0])
    wall = float(diameter_wall.split('х')[-1].replace(',', '.'))
    try:
        price_min = params['цена от 5 тонн'] if params['цена от 5 тонн'] > 0 else 0
    except TypeError:
        price_min = 0
    try:
        price_max = params['цена до 5 тонн'] if params['цена до 5 тонн'] > 0 else 0
    except TypeError:
        price_max = 0

    article_where = 'WHERE '
    article_where += f"standard like '%{standard}%' AND " if standard else ''
    article_where += f"steel like '%{steel}%' AND " if steel else ''
    article_where += f'diameter = {diameter} AND ' if diameter else ''
    article_where += f'wall = {wall} AND' if wall else ''
    article_where = ' '.join(article_where.split()[:-1])
    articles = db.select('article_id', 'chelpipe', article_where, mod='DISTINCT', mode=0)
    if articles:
        for article in articles:
            values = [key, company_id, standard, steel, wall, diameter, None, price_min, price_max, article[0], time, None]
            db.insert('company_price', columns, values)
    else:
        values = [key, company_id, standard, steel, wall, diameter, None, price_min, price_max, None, time, None]
        db.insert('company_price', columns, values)
