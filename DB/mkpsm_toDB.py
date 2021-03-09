import json
import datetime
from tqdm import tqdm
from DB_api import db
import re

with open("../mkpsm.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

columns = 'name, company_id, standard, steel, wall, diameter, city_id, price_min, price_max, article_id, parce_date, url'
time = datetime.datetime.now().timestamp()
company_id = db.select('id', 'company', 'WHERE name = ?', ('"МК Промстройметалл Трейд" ООО',))

if company_id:
    company_id = company_id[0]
else:
    db.insert('company', 'name', ('"МК Промстройметалл Трейд" ООО',))
    company_id = db.cur.lastrowid

find_articles = 0
not_find_articles = 0

for d in tqdm(data):
    if 'Трубы' not in d['name']:
        continue

    standard = d['name'].split('ГОСТ')[-1].strip()
    steel = list()
    if 'сталь' in standard:
        steel = [standard.split(',')[-1].replace('сталь ', '').strip()]
        standard = [standard.split(',')[0].strip()]
    elif ',' in standard:
        standard = standard.split(',')
    else:
        standard = [standard]
    diameter = int(d['size'].split('х')[0])
    wall = [i.replace('м', '').replace(',', '.') for i in re.split(';| ', re.split('Ст.|ст.|\(|ТИП|Гр.', d['size'].split('х')[1])[0].strip()) if i]
    wall = [float(w) if w.replace('.', '', 1).isdigit() else steel.append(w) for w in wall]
    # Пропускать none значения когда буду искать НИС

    if 'ст.' in d['size'] or 'Ст.' in d['size']:
        dirty_steel = re.split('-|,', re.split('сп/пс|ТИП', re.split('Ст.|ст.', d['size'])[-1])[0].strip().replace('м', ''))
        steel.extend(dirty_steel)

    full_where = 'WHERE standard like ? AND steel like ? AND wall = ? AND diameter = ?'
    where_without_steel = 'WHERE standard like ? AND wall = ? AND diameter = ?'
    where_without_wall = 'WHERE standard like ? AND steel like ? AND diameter = ?'
    where_without_steel_and_wall = 'WHERE standard like ? AND diameter = ?'
    articles = []
    if standard:
        for stndrd in standard:
            if wall:
                for wal in wall:
                    if wal is None:
                        pass
                    elif steel:
                        for stl in steel:
                            if steel == 'у':
                                pass
                            else:
                                articles = db.select('article_id', 'chelpipe', full_where,
                                                     (f'%{stndrd}%', f'%{stl.strip()}%', wal, diameter), mod='DISTINCT', mode=0)
                                if articles:
                                    for article in articles:
                                        values = (d['name'], company_id, stndrd, stl.strip(), wal,
                                                  diameter, None, d['price'], None, article[0], time, None)
                                        db.insert('company_price', columns, values)
                                else:
                                    values = (d['name'], company_id, stndrd, stl.strip(), wal,
                                              diameter, None, d['price'], None, None, time, None)
                                    db.insert('company_price', columns, values)

                    else:
                        articles = db.select('article_id', 'chelpipe', where_without_steel,
                                             (f'%{stndrd}%', wal, diameter), mod='DISTINCT', mode=0)
                        if articles:
                            for article in articles:
                                values = (d['name'], company_id, stndrd, None, wal,
                                          diameter, None, d['price'], None, article[0], time, None)
                                db.insert('company_price', columns, values)
                        else:
                            values = (d['name'], company_id, stndrd, None, wal,
                                      diameter, None, d['price'], None, None, time, None)
                            db.insert('company_price', columns, values)

            else:
                if steel:
                    for stl in steel:
                        if steel == 'у':
                            pass
                        else:
                            articles = db.select('article_id', 'chelpipe', where_without_wall,
                                                 (f'%{stndrd}%', f'%{stl.strip()}%', diameter), mod='DISTINCT', mode=0)
                            if articles:
                                for article in articles:
                                    values = (d['name'], company_id, stndrd, stl.strip(), None,
                                              diameter, None, d['price'], None, article[0], time, None)
                                    db.insert('company_price', columns, values)
                            else:
                                values = (d['name'], company_id, stndrd, stl.strip(), None,
                                          diameter, None, d['price'], None, None, time, None)
                                db.insert('company_price', columns, values)
