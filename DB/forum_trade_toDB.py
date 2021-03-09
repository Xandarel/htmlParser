import json
import datetime
from DB_api import db

with open("../forum_trade.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

company_data = db.select('id', 'company', 'WHERE name = ?', ('"Феррум Трейд" ООО',))

if company_data:
    company_id = company_data[0]
    company_url = company_data[-1]
else:
    db.insert('company', 'name', ('"Феррум Трейд" ООО',))
    company_id = db.cur.lastrowid

for d in data:
    city_id = db.select('id', 'city', 'WHERE name = ?', (d['region'].lower(),))

    if city_id:
        city_id = city_id[0]
    else:
        db.insert('city', 'name', (d['region'].lower(),))
        city_id = db.cur.lastrowid

    where = 'WHERE '
    values = list()
    if d['standard']:
        where += 'standard like ? AND '
        values.append('%' + d['standard'] + '%')
    where += 'diameter = ? AND wall = ? AND  steel like ? '
    steel = '%' + d['steel'] + '%'
    values.extend((d['diameter'], d['wall'], steel))
    articles = db.select('article_id', 'chelpipe', where, tuple(values), 'DISTINCT', 0)

    column = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, article_id, parce_date'
    if articles:
        for article in articles:
            time = datetime.datetime.now().timestamp()
            values = (d['name'], company_id, d['standard'], d['steel'], d['wall'],
                      d['diameter'], city_id, d['price'], article[0], time)
            db.insert('company_price', column, values)
    else:
        time = datetime.datetime.now().timestamp()
        values = (d['name'], company_id, d['standard'], d['steel'], d['wall'],
                  d['diameter'], city_id, d['price'], None, time)
        db.insert('company_price', column, values)
