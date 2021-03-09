import pandas as pd
import os
import sqlite3
from DB_insert import find_city, add_article, get_production_method, insert_chelpipe, get_steel, get_production_method
import datetime
from tqdm import tqdm
from natasha import MorphVocab, AddrExtractor


def chelpipe_from_csv():
    type_dict = {'Холоднодеформированные трубы': 'х/д',
                 'Горячедеформированные трубы': 'г/д',
                 'Электросварные трубы': 'ЭСВ',
                 'Не указано': None}

    morph_vocab = MorphVocab()
    addr_extractor = AddrExtractor(morph_vocab)

    path = r'\\chl-vm-aicenter.chtpz.ru\Projects\parsing_price\data'
    name = r'\price_td_uts.csv'
    df = pd.read_csv(fr'{path}{name}', comment='#', sep=';', error_bad_lines=False)

    with sqlite3.connect(r'front/db_test6.sqlite') as connection:
        con = connection
    cur = con.cursor()
    time = datetime.datetime.now().timestamp()
    first = True
    for index in tqdm(range(df.shape[0])):
        name = df.loc[index]['НаименованиеНоменклатуры']
        standards = df.loc[index]['ГОСТ'].split(',')
    #     print(df.loc[index]['МаркаСтали'])
        steel_id = get_steel(df.loc[index]['МаркаСтали'], cur, con)
        diameter = df.loc[index]['Диаметр']
        wall = df.loc[index]['Стенка']
        production_method_id = get_production_method(type_dict[df.loc[index]['ТипПроизводства']], cur, con)
        city_id = find_city(df.loc[index]['Склад'], cur, con, addr_extractor)
        price_min = df.loc[index]['ЦенаЗаТонну'] * 1.2
        price_max = df.loc[index]['ЦенаЗаТонну2'] * 1.2
        article_id = add_article(int(df.loc[index]['КодНИС']), cur, con)
        for standard in standards:
            data = [name, standard.strip(), steel_id, diameter, wall, city_id, price_min,
                    price_max, article_id, time, production_method_id]
            insert_chelpipe(data, cur, con, first)
            if first:
                first = False
