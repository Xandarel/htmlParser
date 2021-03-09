import sqlite3
import datetime


file_index = 0


def find_city(text: str, cur, con, addr_extractor):
    city = addr_extractor.find(text)
    if city:
        city = city.fact.parts[0].value
    else:
        return None
    return get_city_id(city, con, cur)


def add_article(article, cur, con):
    cur.execute(f"""SELECT id 
                    FROM articles
                    WHERE article = ?""", (article,))
    article_id = cur.fetchone()
    if article_id:
        return article_id[0]
    else:
        cur.execute(f"""INSERT INTO articles (article)
                        VALUES (?)""", (article,))
        con.commit()
        return cur.lastrowid


def get_company_id(company_name: str, cur, con):
    cur.execute(f"""SELECT id 
                    FROM company 
                    WHERE name = ?""", (company_name,))
    company_id = cur.fetchone()
    if company_id:
        company_id = company_id[0]
    else:
        cur.execute("""INSERT INTO company (name) VALUES (?)""", (company_name,))
        con.commit()
        company_id = cur.lastrowid
    return company_id


def get_production_method(method: str, cur, con):
    if method:
        cur.execute("""SELECT id 
                        FROM production_method
                        WHERE method = ?""", (method,))
        method_id = cur.fetchone()
        if method_id:
            method_id = method_id[0]
        else:
            cur.execute("""INSERT INTO production_method (method) VALUES (?)""", (method,))
            con.commit()
            method_id = cur.lastrowid
    else:
        method_id = None
    return method_id


def get_city_id(city: str, con, cur):
    if city:
        cur.execute("""SELECT id 
                        FROM city
                        WHERE name = ?""", (city.lower(),))
        city_id = cur.fetchone()
    else:
        return None

    if city_id:
        city_id = city_id[0]
    else:
        cur.execute("""INSERT INTO city (name) VALUES (?)""", (city.lower(),))
        con.commit()
        city_id = cur.lastrowid
    return city_id


def get_articles(data: dict, cur, method_id, city_id):
    where = "WHERE "
    if 'standard' in data.keys():
        if data['standard']:
            where += f"standard like '{data['standard']}%' AND "
    if 'steel' in data.keys():
        if data['steel']:
            where += f"steel_id = {data['steel']} AND "
    if 'diameter' in data.keys():
        if data['diameter']:
            where += f"diameter = {data['diameter']} AND "
    if 'wall' in data.keys():
        if data['wall']:
            where += f"wall = {data['wall']} AND "
    if method_id:
        where += f"method_id = {method_id} AND "
    if city_id:
        where += f"city_id = {city_id} AND "
    where = ' '.join(where.split()[:-1])
    # print(where)
    cur.execute(f"""SELECT DISTINCT article_id, price_min, price_max
                    FROM chelpipe
                    {where}""")
    articles = cur.fetchall()
    return articles


def get_steel(steel, cur, con):
    if steel:
        cur.execute(f"""SELECT id
                        FROM steels
                        WHERE steel = ?""", (steel,))
    else:
        return None
    steel_id = cur.fetchone()
    if steel_id:
        return steel_id[0]
    else:
        cur.execute(f"""INSERT INTO steels (steel)
                        VALUES (?)""", (steel,))
        con.commit()
        return cur.lastrowid


def insert_data(company_name: str, data: dict, soup):
    time = datetime.datetime.now().timestamp()
    with sqlite3.connect('front/db_test6.sqlite') as connection:
        con = connection
    cur = con.cursor()
    company_id = get_company_id(company_name, cur, con)
    if 'production_method' in data.keys():
        if data['production_method']:
            method_id = get_production_method(data['production_method'], cur, con)
        else:
            method_id = None
    else:
        method_id = None
    city_id = get_city_id(data['city'], con, cur)
    data['steel'] = get_steel(data['steel'], cur, con)
    articles = get_articles(data, cur, method_id, city_id)

    columns = '(name, company_id, standard, steel_id, wall, diameter, city_id, price_min, price_max, ' \
              'article_id, parce_date, url, method_id, file_index)'
    columns_lite = '(name, company_id, standard, steel_id, wall, diameter, city_id, price_min, ' \
                   'article_id, parce_date, url, method_id, file_index)'
    global file_index
    if articles:
        for article in articles:
            dumping_check = data['price_min'] < article[1]
            if dumping_check:
                print('here')
                save_html(soup, company_name, file_index)
                file_index += 1
            elif 'price_max' in data.keys() and article[2]:
                dumping_check = data['price_max'] < article[2]
                if dumping_check:
                    print('here2')
                    save_html(soup, company_name, file_index)
                    file_index += 1
            if 'price_max' in data.keys():
                cur.execute(f"""INSERT INTO company_price {columns}
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (data['name'], company_id, data['standard'], data['steel'], data['wall'],
                             data['diameter'], city_id, data['price_min'], data['price_max'], article[0],
                             time, data['url'], method_id, file_index if dumping_check else None))
            else:
                cur.execute(f"""INSERT INTO company_price {columns_lite}
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (data['name'], company_id, data['standard'], data['steel'], data['wall'],
                             data['diameter'], city_id, data['price_min'], article[0],
                             time, data['url'], method_id, file_index if dumping_check else None))
            con.commit()
            index = cur.lastrowid
    else:
        if 'price_max' in data.keys():
            cur.execute(f"""INSERT INTO company_price {columns}
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (data['name'], company_id, data['standard'], data['steel'], data['wall'],
                         data['diameter'], city_id, data['price_min'], data['price_max'], None,
                         time, data['url'], method_id, None))
        else:
            cur.execute(f"""INSERT INTO company_price {columns_lite}
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (data['name'], company_id, data['standard'], data['steel'], data['wall'],
                         data['diameter'], city_id, data['price_min'], None,
                         time, data['url'], method_id, None))
        con.commit()


def insert_chelpipe(data, cur, con, clear):
    if clear:
        cur.execute("""DELETE FROM chelpipe""")
        con.commit()
    columns = '(name, standard, steel_id, diameter, wall, city_id, price_min, price_max, article_id, parse_date, method_id)'
    cur.execute(f"""INSERT INTO chelpipe {columns}
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                tuple(data))
    con.commit()


def save_html(html, company_name: str, index):
    bracer = '"'
    empty = ''
    try:
        with open(rf'Отклонения/{company_name.replace(bracer, empty)}-{index}.html', 'w') as f:
            f.write(html)
    except UnicodeEncodeError:
        with open(rf'Отклонения/{company_name.replace(bracer, empty)}-{index}.html', 'w', encoding='utf-8') as f:
            f.write(html)
