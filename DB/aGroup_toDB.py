import json
import datetime
from tqdm import tqdm
from DB_api import db

with open("../aGroup3.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

time = datetime.datetime.now().timestamp()
carbon = db.select('name', 'carbon_steel', mode=0)
carbon = [i[0] for i in carbon]
company_id = db.select('id', 'company', 'WHERE name = ?', ('А Групп',))
if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('А Групп',))
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

    region = d['city'].lower()
    city_id = db.select('id', 'city', 'WHERE name = ?', (region,))

    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (region,))
        city_id = db.cur.lastrowid

    if '/' in d['standard']:
        standard = d['standard'].split('/')
    else:
        standard = [d['standard'].strip()]

    steel = d['steel'].replace('Ст', '')
    if '-' in steel and '17Г1С' not in steel and '09Г2С' not in steel:
        steel = steel.split('-')
    else:
        steel = [steel]

    wall = d['wall']
    diameter = d['diameter']
    where_with_steel = 'WHERE standard like ? AND steel like ? AND wall = ? AND diameter = ?'
    where_without_steel = 'WHERE standard like ? AND wall = ? AND diameter = ?'
    article_id = list()

    for s in standard:
        select_s = '%' + s.strip() + '%'
        for st in steel:
            wall_where = wall
            if st:
                select_st = '%' + st.strip() + '%'
                article_id.extend(db.select('article_id', 'chelpipe', where_with_steel,
                                            (select_s, select_st, wall_where, diameter), 'DISTINCT', 0))
            else:
                article_id.extend(db.select('article_id', 'chelpipe', where_without_steel,
                                            (select_s, wall_where, diameter), 'DISTINCT', 0))

    columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, article_id, parce_date, url, method_id'
    if article_id:
        for art_id in article_id:
            for s in steel:
                values = (d['name'], company_id, d['standard'] if d['standard'] else None, s if s else None,
                          d['wall'], diameter, city_id, d['price'], art_id[0], time, d['url'], method_id)
                db.insert('company_price', columns, values)
    else:
        for s in steel:
            values = (d['name'], company_id, d['standard'] if d['standard'] else None, s if s else None,
                      d['wall'], diameter, city_id, d['price'], None, time, d['url'], method_id)
            db.insert('company_price', columns, values)
