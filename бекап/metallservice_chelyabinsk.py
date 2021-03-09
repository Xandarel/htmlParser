from bs4 import BeautifulSoup
import json
from selenium import webdriver
from parsing import get_html
import re
import urllib3
from datetime import datetime
import os
import psutil


start_time = datetime.now()
urllib3.disable_warnings()


def find_end_type(product, sep):
    for p in range(len(product)):
        if product[p].find(sep) > 0:
            return p


options = webdriver.ChromeOptions()
# options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=options)

page = '/PageN/'
main_list = list()
base_url = 'https://mc.ru'
catalog = '/products/chelyabinsk'
html = get_html(base_url + catalog)
soup = BeautifulSoup(html, 'lxml')

browser.get(base_url + catalog)
browser.implicitly_wait(20)
browser.find_element_by_id('chosenCityName').click()
element = browser.find_element_by_class_name('FilialsUl')
element_html = element.get_attribute('outerHTML')
browser.quit()
a = BeautifulSoup(element_html, 'lxml')
ass = a.find_all('a')
for a1 in ass:
    html = get_html(base_url + a1.get('href'))
    soup = BeautifulSoup(html, 'lxml')
    # получение списка продуктов компании
    div = soup.find('div', {'class': 'productsMenuBlock prokat_trub'})
    main_ul = div.find_all('li')
    price_list = list()
    for mul in main_ul:
        ul = mul.find_all('ul', {"class": "inserted"})
        if ul:
            for a2 in ul:
                href = a2.find_all('a')
                for url in href:
                    if url.get('href') is not None \
                            and 'Трубы' in url.text\
                            and 'оцинкованные' not in url.text \
                            and 'квадратные' not in url.text and \
                            'прямоугольные' not in url.text:
                        price_list.append(url.get('href'))
        else:
            href = mul.find('a')
            if href.get('href') is not None\
                    and 'Трубы' in href.text\
                    and 'оцинкованные' not in href.text \
                    and 'квадратные' not in href.text and \
                    'прямоугольные' not in href.text:
                price_list.append(href.get('href'))
    # print(price_list)
    for url in price_list:
        page_num = 1
        while True:
            if page_num == 1:
                new_url = base_url + url
            else:
                new_url = base_url + url + page + str(page_num)
            html = get_html(new_url)
            print(new_url)
            # time.sleep(2)
            try:
                soup = BeautifulSoup(html, 'lxml')
            except:
                soup = BeautifulSoup(html, 'lxml')
            table = soup.find_all('tbody', id='grid_tab')
            if table:
                tr = table[0].find_all('tr')
                for t in tr:
                    tds = t.find_all('td')
                    product = tds[0].text.replace('→', '').strip().split()
                    if 'Трубы' not in product and 'трубы' not in product:
                        continue
                    production_method = re.search(r'\w/\w|ЭСВ', tds[0].text.replace('→', '').strip())
                    production_method = production_method[0] if production_method else None
                    # print(production_method)
                    # print(f'\t{product}')
                    sep = ('x', 'х')
                    x_element = find_end_type(product, sep[0])
                    try:
                        tube_type = ' '.join(product[1:x_element])
                        # print(tube_type)
                        wall = product[x_element].split(sep[0])[-1]
                    except TypeError:
                        x_element = find_end_type(product, sep[-1])
                        wall = product[x_element].split(sep[-1])[-1]
                        tube_type = ' '.join(product[1:x_element])

                    diameter = float(tds[1].text.strip().replace(',', '.'))
                    steel = tds[2].text.strip().replace('Ст', '')
                    span = tds[4].find('span')
                    name = tds[0].text.replace('→', '').strip()
                    standard = re.search(r'ГОСТ \d*-\d*', name)
                    standard = standard[0].replace('ГОСТ', '').strip() if standard else None

                    if span:
                        region = tds[4].text.replace(span.text, '').strip()
                    else:
                        region = tds[4].text.strip()
                    if region == 'Н.Новгород':
                        region = 'нижний новгород'
                    price_max = tds[5].text.strip().replace(u'\xa0', u'')
                    price_min = tds[7].text.strip().replace(u'\xa0', u'')
                    # print(tds[5], tds[7])
                    # print(price_min, price_max)
                    # input()
                    parse_dict = {'name': tds[0].text.replace('→', '').strip(),
                                  'type': tube_type,
                                  'standard': standard,
                                  'wall': wall,
                                  'diameter': diameter,
                                  'steel': steel,
                                  'region': region,
                                  'price_min': price_min,
                                  'price_max': price_max,
                                  'url': new_url,
                                  'production_method': production_method}
                    main_list.append(parse_dict)
                page_num += 1
            else:
                break

json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('metallservice_chelyabinsk.json', "w",  encoding='utf-8') as file:
    file.write(json_list)

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
print('memory use:', memoryUse)
end_time = datetime.now()
print(f'Duration: {end_time - start_time}')
