import json
import datetime
from tqdm import tqdm
from DB_api import db

columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, price_max, article_id, parce_date, url, method_id'

with open("../dmk2.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

company_id = db.select('id', 'company', 'WHERE name = ?', ('"Дальневосточная металлургическая компания-Снаб" ООО',))
if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"Дальневосточная металлургическая компания-Снаб" ООО',))
    company_id = db.cur.lastrowid
time = datetime.datetime.now().timestamp()
for d in tqdm(data):
    region = d['region'].lower()
    city_id = db.select('id', 'city', 'WHERE name = ?', (region,))
    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (region,))
        city_id = db.cur.lastrowid
    name = d['type']
    diameter = d['diameter']
    wall = d['wall']
    max_price = 0 if d['max_price'] == '' else d['max_price']
    min_price = 0 if d['min_price'] == '' else d['min_price']
    url = d['url'] + ' '

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

    article_where = 'WHERE '
    if diameter:
        article_where += f'diameter = {diameter} AND '
    if wall:
        article_where += f'wall = {wall} AND '
    article_where = ' '.join(article_where.split()[:-1])
    articles = db.select('article_id', 'chelpipe', article_where, mod='DISTINCT', mode=0)
    if articles:
        for article in articles:
            values = [name, company_id, None, None, wall, diameter, city_id, min_price, max_price, article[0], time, url, method_id]
            db.insert('company_price', columns, values)
    else:
        values = [name, company_id, None, None, wall, diameter, city_id, min_price, max_price, None, time, url, method_id]
        db.insert('company_price', columns, values)
