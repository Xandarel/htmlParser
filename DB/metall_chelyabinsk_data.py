import datetime
import json
from tqdm import tqdm
from DB_api import db

with open("../metallservice_chelyabinsk.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

company_id = db.select('id', 'company', 'WHERE name = ?', ('"Металлсервис" ОАО',))
time = datetime.datetime.now().timestamp()
if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"Металлсервис" ОАО',))
    company_id = db.cur.lastrowid

for d in tqdm(data):

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

    region = d['region'].lower()
    if region == 'Н.Новгород':
        region = 'нижний новгород'
    region_id = db.select('id', 'city', 'WHERE name = ?', (region,))

    if d['price_min']:
        try:
            price_min = float(d['price_min'].replace(u'\xa0', u'').replace('спеццена', ''))
        except ValueError:
            price_min = 0
    else:
        price_min = 0
    if d['price_max']:
        try:
            price_max = float(d['price_max'].replace(u'\xa0', u'').replace('спеццена', ''))
        except ValueError:
            price_max = 0
    else:
        price_max = 0

    wall = float(d['wall'].strip().replace(',', ''))
    if region_id:
        region_id = region_id[0]
    else:
        db.insert('city', 'name', (d['region'].lower(),))
        region_id = db.cur.lastrowid

    where = 'WHERE '
    values = list()

    if d['steel']:
        where += 'steel like ? AND '
        values.append(f"%{d['steel'].strip()}%")

    where += 'wall = ? AND diameter = ?'
    values.extend((wall, d['diameter']))

    articles = db.select('article_id', 'chelpipe', where, tuple(values), 'DISTINCT', 0)
    columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, ' \
              'price_max, article_id, parce_date, url,  method_id'

    if articles:
        for article in articles:
            values = (d['name'], company_id, None, d['steel'] if d['steel'] else None, wall, d['diameter'],
                      region_id, price_min, price_max, article[0], time, d['url'], method_id)
            db.insert('company_price', columns, values)
    else:
        values = (d['name'], company_id, None, d['steel'] if d['steel'] else None, wall, d['diameter'],
                  region_id, price_min, price_max, None, time, d['url'], method_id)
        db.insert('company_price', columns, values)
