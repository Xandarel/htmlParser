from bs4 import BeautifulSoup
import json
import re
from parsing import get_html
from datetime import datetime
import os
import psutil


start_time = datetime.now()

base_url = 'http://dmk.su/truby-i-otvody-jshop/truby-tselnotyanutye-besshovnye'
parth_url = 'http://dmk.su'
all_url = '?limit=99999'
main_list = list()
html = get_html(base_url + all_url)
soup = BeautifulSoup(html, 'lxml')
li = soup.find_all('li', {'class': 'item-169 active deeper parent'})[0]
ul = li.find_all('ul', {'class': 'nav-child unstyled small'})[0]
li = ul.find_all('li')
for l in li:
    a = l.find('a')
    if 'профильная' in a.text or 'оцинкованные' in a.text or 'Трубы' not in a.text:
        continue
    if 'электросварные' in a.text:
        zinc = 1
    else:
        zinc = 0
    new_url = parth_url + a.get('href') + all_url
    html = get_html(new_url)
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find_all('div', {'class': 'products-in-cat'})
    for d in div:
        info = d.find('a')
        info_href = info.get('href')
        html = get_html(parth_url + info_href)
        print(parth_url + info_href)
        soup = BeautifulSoup(html, 'lxml')
        product_div = soup.find('div', {'class': 'tab-cont active'})
        p_data = product_div.get_text(separator='\n').strip().split('\n')
        h1 = soup.find('h1', {'class': '456'}).text.strip().split()
        h1_text = soup.find('h1', {'class': '456'}).text.strip()

        if len(h1) == 6:
            product_type = h1[0] + ' ' + h1[1]
            diameter_wall = re.search(r'[+-]?([0-9]*[,])?[0-9]+ ?х ?[+-]?([0-9]*[,])?[0-9]+', h1_text)[0].split('х')
            try:
                diameter = float(diameter_wall[0].replace(',', '.'))
            except:
                diameter = None
            if diameter < 0:
                diameter = diameter * (-1)
            try:
                wall = float(diameter_wall[-1].replace(',', '.'))
            except:
                wall = None
        else:
            product_type = h1[0]
            if 'Труба' in product_type:
                try:
                    diameter = float(h1[1].split('х')[0])
                except:
                    diameter = None
                if diameter < 0:
                    diameter = diameter * (-1)
                try:
                    wall = float(h1[1].split('х')[-1].replace(',', '.'))
                except:
                    wall = None
            else:
                continue
        try:
            price = float(soup.find('span', {'itemprop': 'price'}).text.strip())
        except:
            price = 0
        try:
            max_price = float(p_data[3].strip().replace(' ', '').replace(u'\xa0', ''))
        except:
            max_price = 0
        try:
            min_price = float(p_data[5].strip().replace(' ', '').replace(u'\xa0', ''))
        except:
            min_price = 0
        if p_data[6] == 'Марка стали/ ГОСТ:':
            standard = p_data[7].split()[2]
            steel = p_data[7].split()[3].split('.')[1]
            main_list.append({'region': 'хабаровск',
                              'type': product_type,
                              'diameter': diameter,
                              'wall': wall,
                              'price': price,
                              'max_price': max_price,
                              'min_price': min_price,
                              'url': parth_url + info_href,
                              'standard': standard,
                              'steel': steel})
        else:
            main_list.append({'region': 'хабаровск',
                              'type': product_type,
                              'diameter': diameter,
                              'wall': wall,
                              'price': price,
                              'max_price': max_price,
                              'min_price': min_price,
                              'url': parth_url + info_href,
                              'production_method': 'ЭСВ' if zinc else None})
        diameter = None
        wall = None
json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('dmk2.json', "w",  encoding='utf-8') as file:
    file.write(json_list)

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
print('memory use:', memoryUse)
end_time = datetime.now()
print(f'Duration: {end_time - start_time}')


