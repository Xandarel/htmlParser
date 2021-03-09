from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from parsing import get_html
from datetime import datetime
import os
import psutil


start_time = datetime.now()

options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=options)
browser.implicitly_wait(2)
urls = ('http://www.metallotorg.ru/info/metalloprokat/truba_vodogazoprovodnaya_vgp/',
        'http://www.metallotorg.ru/info/metalloprokat/truba_elektrosvarnaya/',
        'http://www.metallotorg.ru/info/metalloprokat/truba_besshovnaya_stalnaya/')
main_list = list()
for url in urls:
    iterator = 1
    browser.get(url)
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    select = soup.find('select', id='se_name')
    options = select.find_all('option')
    for option in range(1, len(options)):
        iterator = 1
        while True:
            print(f'pup{iterator}')
            table = browser.find_element_by_id('TheBody')
            table_html = table.get_attribute('outerHTML')
            table_soup = BeautifulSoup(table_html, 'lxml')
            trs = table_soup.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                type_tube = tds[0].text.strip()
                production_method = None if 'ЭС' not in type_tube else 'ЭСВ'
                diameter = tds[1].text.strip().split('*')[0].strip()
                wall = tds[1].text.strip().split('*')[-1].strip()
                standards = tds[3].text\
                                  .strip()\
                                  .split('ГОСТ')[-1]\
                                  .strip()\
                                  .replace('СеверСталь', '')\
                                  .replace('Скидка', '')\
                                  .replace('Севесталь', '')\
                                  .replace('Северсталь', '')\
                                  .strip()\
                                  .split(',')
                availability = tds[5].text.strip()
                max_price = tds[6].text.strip()
                min_price = tds[8].text.strip()
                branch = tds[-2].text.strip()
                for standard in standards:
                    main_list.append({'type': type_tube,
                                      'diameter': diameter,
                                      'wall': wall,
                                      'standard': standard,
                                      'availability': availability,
                                      'max_price': max_price,
                                      'min_price': min_price,
                                      'branch': branch,
                                      'url': url,
                                      'production_method': production_method})
                # Считывание таблицы
            try:
                iterator += 1
                browser.find_element_by_link_text(f'{iterator}').click()
            except:
                element = Select(browser.find_element_by_id('se_name'))
                element.select_by_index(option)
                break
json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('metallotorg.json', "w",  encoding='utf-8') as file:
    file.write(json_list)

browser.quit()

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
print('memory use:', memoryUse)
end_time = datetime.now()
print(f'Duration: {end_time - start_time}')


