from bs4 import BeautifulSoup
import json
from selenium import webdriver
from parsing import get_html
import time
import urllib3
from datetime import datetime
import os
import psutil


start_time = datetime.now()

urllib3.disable_warnings()

options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=options)

base_url = 'https://abakan.spk.ru/'
https = 'https:'
html = get_html(base_url)
browser.get(base_url)
browser.implicitly_wait(2)
element = browser.find_element_by_class_name('top_line__city-link')
element.click()
element = browser.find_element_by_class_name('city__list-wrap')

generated_html = element.get_attribute('outerHTML')
soup = BeautifulSoup(generated_html, 'lxml')
a = soup.find_all('a')
main_list = list()

for href in a:
    region = href.text.strip()
    region_url = https + href.get('href') + 'catalog/metalloprokat/trubniy-prokat/'
    browser.get(region_url)
    element = browser.find_element_by_class_name('catalog')
    div = element.get_attribute('outerHTML')
    soup = BeautifulSoup(div, 'lxml')
    product_catalog = soup.find_all('a', {'class': 'catalog__link'})
    for product in product_catalog:
        if 'профильная' in product.text:
            continue
        product_url = https + href.get('href') + product.get('href')[1:]
        print(product_url)
        try:
            browser.get(product_url)
        except:
            time.sleep(2)
            browser.get(product_url)
        element = browser.find_element_by_class_name('col-md-9')
        data = element.get_attribute('outerHTML')
        data_soup = BeautifulSoup(data, 'lxml')
        data_div = data_soup.find_all('div', {'class': 'card-card-simplified-view product-card'})
        for dd in data_div:
            dd_a = dd.find_all('a', {'class': 'product-card__title-link'})[0].text
            dd_price = dd.find_all('div', {'class': 'product-card__size-bold'})[0].text
            float_price = ''
            for price in dd_price:
                if price.isdigit() or price == ',':
                    float_price += price
            if float_price != '':
                float_price = float(float_price.replace(',', '.'))
            else:
                float_price = 0

            dd_array = dd_a.split()
            type = dd_array[0] + ' ' + dd_array[1]

            if 'Труба' not in type:
                continue

            wall = ''
            for t in range(2, len(dd_array)):
                wall += dd_array[t] + ' '
            wall = wall.strip().split()
            try:
                wall_json = float(wall[-1])

                if wall_json > 1000:
                    wall_json = float(wall[-2])
            except ValueError:
                try:
                    wall_json = float(wall[-2])
                except ValueError:
                    wall_json = None
            if 'оцинкованная' in type or 'профильная' in type:
                continue
            elif 'электросварная' in type:
                production_method = 'ЭСВ'
            elif 'холоднодеформированная' in type:
                production_method = 'х/д'
            else:
                production_method = None
            main_list.append({'type': type,
                              'region': region,
                              'diameter': wall[0].replace('ДУ', '').replace('ОЦ', ''),
                              'wall': wall_json,
                              'price': float_price,
                              'url': product_url,
                              'production_method': production_method})

json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('spk2.json', "w",  encoding='utf-8') as file:
    file.write(json_list)
browser.quit()

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
print('memory use:', memoryUse)
end_time = datetime.now()
print(f'Duration: {end_time - start_time}')
