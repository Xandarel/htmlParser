import datetime
import json
from tqdm import tqdm
from DB_api import db

with open("../metallotorg.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)
time = datetime.datetime.now().timestamp()
company_id = db.select('id', 'company', 'WHERE name = ?', ('"Металлоторг" АО',))

if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"Металлоторг" АО',))
    company_id = db.cur.lastrowid
for d in tqdm(data):
    article_where = 'WHERE '
    article_data = list()
    name = 'Труба ' + d['type']
    diameter = float(d['diameter'].replace(',', '.'))
    standard = d['standard'].replace('Северсталь', '')
    if not standard:
        standard = None
    wall = float(''.join(filter(str.isdigit, d['wall'].replace(',', '.'))))
    max_price = float(d['max_price'])
    min_price = float(d['min_price'])
    city = d['branch']

    if standard:
        if '-' in standard and 'ТУ' not in standard:
            where_standard = standard.split('-')[0]
            article_where += f"standard like '{where_standard.strip()}%' AND "
        else:
            article_where += f"standard like '{standard.strip()}%' AND "
    article_where += 'wall = ? AND diameter = ?'
    article_data.extend([wall, diameter])
    articles_id = db.select('article_id', 'chelpipe', article_where, tuple(article_data), mode=0)

    if '(' in city:
        city = city.split()[-1].replace('(', '').replace(')', '')

    city_id = db.select('id', 'city', 'WHERE name = ?', (city.lower(),))

    method = d['production_method']
    if method:
        method_id = db.select('id', 'production_method', 'WHERE method = ?', (method,))
        if method_id:
            method_id = method_id[0]
        else:
            db.insert('production_method', 'method', (method,))
            city_id = db.cur.lastrowid
    else:
        method_id = None

    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (city.lower(),))
        city_id = db.cur.lastrowid

    columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, price_max, article_id, parce_date, url, method_id'
    if articles_id:
        for article_id in articles_id:
            values = (name, company_id, standard, None, wall, diameter, city_id, min_price, max_price, article_id[0], time, d['url'], method_id)
            db.insert('company_price', columns, values)
    else:
        values = (name, company_id, standard, None, wall, diameter, city_id, min_price, max_price, None, time, d['url'], method_id)
        db.insert('company_price', columns, values)

