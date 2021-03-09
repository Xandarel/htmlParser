from bs4 import BeautifulSoup
import json
import re
from parsing import get_html
from datetime import datetime
import os
import psutil
from DB_insert import insert_data


def siber_res():
    start_time = datetime.now()

    json_main_list = list()
    main_dict = dict()
    main_list = list()
    first = True
    base_url = 'http://sr93.ru/prod/#r5'
    html = get_html(base_url)
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find_all('table', {"class": "price"})
    tr = table[0].find_all('tr')
    for t in tr:
        tds = t.find_all('td')

        if 'Лист' in tds[0].text:
            break

        if 'ГОСТ' in tds[0].text:
            full_name = tds[0].text.replace('наверх', '')
            standard_data = full_name.split('ГОСТ')
            full_name = full_name[:full_name.find('ГОСТ')]
            production_method = re.search(r'электросварная|ЭСВ|холоднодеформированная|горячедеформированная', full_name)
            if production_method:
                if production_method[0] == 'электросварная' or production_method[0] == 'ЭСВ':
                    production_method = 'ЭСВ'
                elif production_method[0] == 'холоднодеформированная':
                    production_method = 'х/д'
                elif production_method[0] == 'горячедеформированная':
                    production_method = 'г/д'
            else:
                production_method = None

            if len(standard_data) == 2:
                standard = standard_data[-1].split('ст')[0].strip()
                if 'ст' in standard_data[-1]:
                    steel = standard_data[-1].split('ст')[-1].strip()
                else:
                    if standard == '20295':
                        steel = '10-20; 09Г2С, 17Г1С'
                    else:
                        steel = None
            else:
                standard = standard_data[1] + standard_data[-1].split('ст')[0].strip()
                if 'ст' in standard_data[-1]:
                    steel = standard_data[-1].split('ст')[-1].strip()
                else:
                    steel = None

        if len(tds) == 3 and tds[0].get('class')[0] == 'left':
            td0 = tds[0].text.strip().split('х')
            if len(td0) == 1:
                td0 = tds[0].text.strip().split('x')
                if '-' in td0[0]:
                    diameter = td0[0].split('-')[0]
                    wall = None
                else:
                    diameter = td0[0].strip()
                    wall = None
            elif len(td0) == 2:
                diameter = td0[0].split()[-1]
                if '-' in diameter:
                    diameter = diameter.split('-')[0]
                wall = td0[1].split()[0]
                if '-' in wall:
                    wall = wall.split('-')[0]
            else:
                diameter = td0[0]  # + 'x' + td0[1]
                wall = td0[-1].strip().split()[0]

            if wall == '':
                wall = None
            if wall:
                wall = float(wall.replace(',', '.'))
            max_price = tds[1].text.replace(' ', '')
            min_price = tds[2].text.replace(' ', '')
            if max_price == '':
                max_price = 0
            for s in standard.split(';'):
                if 'оцинкованная' in full_name or 'профильная' in full_name:
                    continue
                for stndrt in s.split(','):
                    if steel:
                        steel_split = re.split(',|;', steel)
                    else:
                        steel_split = None
                    if steel_split:
                        for st_sp in steel_split:
                            dict_data = {'name': full_name.strip(),
                                         'standard': stndrt.strip(),
                                         'steel': st_sp,
                                         'diameter': float(diameter.replace('d ', '')),
                                         'wall': wall,
                                         'price_max': float(max_price),
                                         'price_min': float(min_price),
                                         'city': 'новосибирск',
                                         'url': base_url,
                                         'production_method': production_method}
                            insert_data('"Сибирские ресурсы" ОАО', dict_data, html)
                    else:
                        dict_data = {'name': full_name.strip(),
                                     'standard': stndrt.strip(),
                                     'steel': steel,
                                     'diameter': float(diameter.replace('d ', '')),
                                     'wall': wall,
                                     'price_max': float(max_price),
                                     'price_min': float(min_price),
                                     'city': 'новосибирск',
                                     'url': base_url,
                                     'production_method': production_method}
                        insert_data('"Сибирские ресурсы" ОАО', dict_data, html)
    #             main_list.append(dict_data)
    # json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
    # with open('siberian_resources.json', "w",  encoding='utf-8') as file:
    #     file.write(json_list)


    pid = os.getpid()
    py = psutil.Process(pid)
    memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
    print('memory use:', memoryUse)
    end_time = datetime.now()
    print(f'Duration: {end_time - start_time}')

