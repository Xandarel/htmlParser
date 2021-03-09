import json
import datetime
from tqdm import tqdm
from DB_api import db


with open("../minValue.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)
for d in tqdm(data):
    time = datetime.datetime.now().timestamp()
    region = d['region'].split('.')[-1]

    if region == ' С-ПЕТЕРБУРГ':
        region = 'Санкт-Петербург'
    elif region == 'Н-НОВГОРОД':
        region = 'Нижний Новгород'

    region = region.lower()
    city_id = db.select('id', 'city', 'WHERE name = ?', (region,))

    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (region,))
        city_id = db.cur.lastrowid

    if d['wall_min']:
        wall_min = d['wall_min']
    else:
        wall_min = 0

    if d['wall_max']:
        wall_max = d['wall_max']
    else:
        wall_max = 100

    columns = 'standard, diameter_min, diameter_max, steel, wall_min, wall_max, city_id, price, date_begin'
    values = (d['standard'].replace('ОСТ', ''), d['diameter_min'], d['diameter_max'], d['steel'],
              wall_min, wall_max, city_id, d['price'], time)
    db.insert('MinValue', columns, values)

