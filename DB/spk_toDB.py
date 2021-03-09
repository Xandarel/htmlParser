import json
import datetime
from tqdm import tqdm
from DB_api import db

with open("../spk2.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

company_id = db.select('id', 'company', 'WHERE name = ?', ('"Сталепромышленная компания" АО',))
if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"Сталепромышленная компания" АО',))
    company_id = db.cur.lastrowid

time = datetime.datetime.now().timestamp()
for d in tqdm(data):
    where = 'WHERE '
    values = list()
    name = d['type']
    region = d['region'].lower()
    try:
        diameter = float(d['diameter'])
        where += 'diameter = ? AND '
        values.append(diameter)
    except:
        diameter = None

    if not diameter:
        diameter = None

    wall = d['wall']
    if wall == 0:
        wall = None
    else:
        where += 'wall = ? AND '
        values.append(wall)
    price = d['price']
    if price == '':
        price = 0

    url = d['url']

    city_id = db.select('id', 'city', 'WHERE name = ?', (region,))
    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (region,))
        city_id = db.cur.lastrowid

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

    where = ' '.join(where.split()[:-1])
    article_id = db.select('article_id', 'chelpipe', where, values, 'DISTINCT', 0)
    columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, article_id, parce_date, url, method_id'
    if article_id:
        for art_id in article_id:
            values = [name, company_id, None, None, wall, diameter, city_id, price, art_id[0], time, url, method_id]
            db.insert('company_price', columns, values)
    else:
        values = [name, company_id, None, None, wall, diameter, city_id, price, None, time, url, method_id]
        db.insert('company_price', columns, values)
