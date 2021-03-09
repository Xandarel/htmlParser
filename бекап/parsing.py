import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
from selenium import webdriver
import re
from datetime import datetime
import os
import psutil

start_time = datetime.now()

# ----------------------------------------------------
def get_html(url):
    """
    функция достаёт html по url
    """
    ret = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        r = requests.get(url, headers=headers, verify=False)
        ret = r.text
    except Exception as e:
        print(str(e))

    return ret


def gt_sub_group(url):
    soup = BeautifulSoup(url, 'lxml')
    # ищем таблицу с id='price_list'
    p = soup.find_all('ul', {"class": "price-tree"})
    a = p[0].find_all('a')
    sub_group = list()
    for href in a:
        if 'Труба' in href.text \
                and 'оцинкованная' not in href.text \
                and 'профильная' not in href.text \
                and 'профильные' not in href.text\
                and 'плоскоовальная' not in href.text\
                and 'полуовальная' not in href.text:
            sub_group.append(href.get('href'))
    return sub_group

# ----------------------------------------------------


json_list = list()
if __name__ == '__main__':
    base_url = 'http://www.agrupp.com/pricelist/'
    start_url = '?sub_group=3765'
    sub_group = list()
    sub_group.append('?sub_group=3765')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.implicitly_wait(2)

    browser.get(base_url + start_url)
    active_region = browser.find_element_by_class_name('region-selector')
    active_region.click()

    cities = browser.find_element_by_class_name('region-modal')
    cities = cities.get_attribute('outerHTML')
    cities_soup = BeautifulSoup(cities, 'lxml')
    div = cities_soup.find_all('div')[2:]

    for d in tqdm(div):
        browser.get(base_url + start_url)
        active_region = browser.find_element_by_class_name('region-selector')
        active_region.click()
        new_region = browser.find_element_by_id(d.get('id'))
        new_region.click()
        sub_group.clear()
        sub_group.append('?sub_group=3765')
        # достаём html
        group = gt_sub_group(browser.page_source)
        sub_group += group
        for sg in sub_group:
            browser.get(base_url+sg)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            p = soup.find_all('table', id='price_list')
            row = p[0].find_all('tr')[1:]
            for r in row:
                body = r.find_all('td')
                production_method = re.search(r'\w/\w|электросварная', body[0].text)
                production_method = production_method[0] if production_method else None
                production_method = 'ЭСВ' if production_method == 'электросварная' else production_method
                try:
                    diameter, wall = body[1].text.split('х')
                except ValueError:
                    split = body[1].text.split('х')
                    diameter = split[0]
                    wall = split[-1]
                standard = body[3].text.split('ГОСТ')[-1].strip()
                if standard == 'ТУ':
                    continue
                json_dict = {'name': body[0].text,
                             'diameter': float(diameter.strip().replace(',', '.')),
                             'wall': float(wall.replace(',', '.').strip()),
                             'steel': body[2].text,
                             'standard': standard,
                             'city': body[4].text.replace('Доставка в ', '').strip(),
                             'price': int(body[5].text.replace(u'\xa0', '')),
                             'url': base_url + sg,
                             'production_method': production_method}
                json_list.append(json_dict)
    json_list = json.dumps(json_list,  ensure_ascii=False).replace('},', '},\n')
    browser.quit()
    with open('aGroup3.json', "w",  encoding='utf-8') as file:
        file.write(json_list)

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
print('memory use:', memoryUse)
end_time = datetime.now()
print(f'Duration: {end_time - start_time}')
