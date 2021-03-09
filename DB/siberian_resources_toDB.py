import json
import datetime
import re
from tqdm import tqdm
from DB_api import db

with open('../siberian_resources.json', "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

company_id = db.select('id', 'company', 'WHERE name = ?', ('"Сибирские ресурсы" ОАО',))

if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"Сибирские ресурсы" ОАО',))
    company_id = db.cur.lastrowid

time = datetime.datetime.now().timestamp()
carbon = db.select('name', 'carbon_steel', mode=0)
carbon = [i[0] for i in carbon]
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

    city_id = db.select('id', 'city', 'WHERE name = ?', (d['region'].lower(),))
    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (d['region'].lower(),))
        city_id = db.con.lastrowid
    articles_id = list()
    standard_split = d['standard'].split(',')
    if d['steel']:
        steel_split = re.split(',|-|;', d['steel'])
    else:
        steel_split = []
    for stndrt in standard_split:
        where = 'WHERE standard like ? AND diameter = ?'
        if d['steel']:
            where += ' AND steel like ? '
            for stl in steel_split:
                if stl == 'У':
                    continue
                if d['wall']:
                    wall = float(d['wall'].replace(',', '.'))
                    new_where = where + 'AND wall = ?'
                    values = (f'%{stndrt.strip()}%', d['diameter'], f'%{stl.strip()}%', wall)
                    articles_id.extend(db.select('article_id', 'chelpipe', new_where, values, 'DISTINCT', 0))
                else:
                    values = (f'%{stndrt.strip()}%', d['diameter'], f'%{stl.strip()}%')
                    articles_id.extend(db.select('article_id', 'chelpipe', where, values, 'DISTINCT', 0))

        else:
            if d['wall']:
                new_where = where + 'AND wall = ?'
                wall = float(d['wall'].replace(',', '.'))
                values = (f'%{stndrt.strip()}%', d['diameter'], wall)
                articles_id.extend(db.select('article_id', 'chelpipe', new_where, values, 'DISTINCT', 0))
            else:
                values = (f'%{stndrt}%', d['diameter'])
                articles_id.extend(db.select('article_id', 'chelpipe', where, values, 'DISTINCT', 0))

    columns = 'name, company_id, standard, steel, wall, diameter, city_id, ' \
              'price_min, price_max, article_id, parce_date, url, method_id'
    if articles_id:
        for article in articles_id:  # артикли
            for stndrt in standard_split:  # ГОСТЫ
                if d['steel']:
                    for stl in steel_split:  # Стали
                        if stl == 'У':
                            continue
                        values = (d['full_name'], company_id, stndrt.strip(), stl.strip(), d['wall'],
                                  d['diameter'], city_id, d['min_price'], d['max_price'], article[0], time, d['url'], method_id)
                        db.insert('company_price', columns, values)
                else:
                    values = (d['full_name'], company_id, stndrt.strip(), d['steel'], d['wall'],
                              d['diameter'], city_id, d['min_price'], d['max_price'], article[0], time, d['url'], method_id)
                    db.insert('company_price', columns, values)
    else:
        for stndrt in standard_split:  # ГОСТЫ
            if d['steel']:
                for stl in steel_split:  # Стали
                    if stl == 'У':
                        continue
                    values = (d['full_name'], company_id, stndrt.strip(), stl.strip(), d['wall'],
                              d['diameter'], city_id, d['min_price'], d['max_price'], None, time, d['url'], method_id)
                    db.insert('company_price', columns, values)
            else:
                values = (d['full_name'], company_id, stndrt.strip(), d['steel'], d['wall'],
                          d['diameter'], city_id, d['min_price'], d['max_price'], None, time, d['url'], method_id)
                db.insert('company_price', columns, values)
