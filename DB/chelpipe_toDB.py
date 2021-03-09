import json
import datetime
from tqdm import tqdm
import os
from DB_api import db


files = os.listdir('../chelpipeJsons')
time = datetime.datetime.now().timestamp()
for file in files:
    print(file)
    with open(os.path.join('../chelpipeJsons', file), "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
        for d in tqdm(data):
            region = d['region'].lower()
            if '(' in region:
                region = region.split()[0]

            city_id = db.select('id', 'city', 'WHERE name = ?', (region,))
            if city_id:
                city_id = city_id[0]
            else:
                db.insert('city', 'name', (region,))
                city_id = db.cur.lastrowid

            article_id = db.select('id', 'articles', 'WHERE article = ?', (int(d['article']),))
            if article_id:
                article_id = article_id[0]
            else:
                db.insert('articles', 'article', (int(d['article']),))
                article_id = db.cur.lastrowid

            method_id = db.select('id', 'production_method', 'WHERE method = ?', (d['production_method'],))
            if method_id:
                method_id = method_id[0]
            else:
                db.insert('production_method', 'method', (d['production_method'],))
                method_id = db.cur.lastrowid

            columns = 'name, standard, steel, diameter, wall, city_id, price_min, price_max, ' \
                      'article_id, type_of_length, parse_date, method_id'
            values = (d['type_tube'], d['standard'], d['steel'], d['diameter'], d['wall'],
                      city_id, d['price_min'],  d['price_max'], article_id, d['type_of_length'], time, method_id)
            db.insert('chelpipe', columns, values)

