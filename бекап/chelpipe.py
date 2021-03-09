from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium import common
from tqdm import tqdm
from parsing import get_html


options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=options)

base_url = 'https://market.chelpipe.ru/'
base_html = get_html(base_url)

browser.implicitly_wait(0.5)
browser.get(base_url)
div = browser.find_element_by_class_name('main__catalog')

div_html = div.get_attribute('outerHTML')
soup = BeautifulSoup(div_html, 'lxml')
aas = soup.find_all('a', {'class': 'catalog-list-item__link'})
main_list = list()
for a in tqdm(aas):
    page = 1
    new_url = (base_url + a.get('href')).replace('//', '/')
    browser.get(new_url)
    while True:
        try:
            table = browser.find_element_by_class_name('table__main')
        except:
            break

        table_html = table.get_attribute('outerHTML')
        table_soup = BeautifulSoup(table_html, 'lxml')
        div_row = table_soup.find_all('div', {'class': 'table-row'})
        for dr in tqdm(div_row):

            page_product = dr.find('a').get('href')

            try:
                browser.get((base_url + page_product).replace('//', '/'))
            except common.exceptions.TimeoutException:
                print('TimeoutException')
                print((base_url + page_product).replace('//', '/'))
                browser.get((base_url + page_product).replace('//', '/'))
            try:
                product_page = browser.find_element_by_class_name('product-card-main__stats').get_attribute('outerHTML')
            except common.exceptions.NoSuchElementException:
                print('NoSuchElementException')
                print(browser.current_url)
                product_page = browser.find_element_by_class_name('product-card-main__stats').get_attribute('outerHTML')
            cart = BeautifulSoup(product_page, 'lxml')
            data = cart.find_all('div', {'class': 'product-card-main__stats-item-value'})
            article = data[-1].text
            type_of_length = data[-2].text.strip()

            row = dr.find_all('div', {'class': 'table-row__item-value'})

            for_tube = dr.find('div', {'class': 'table-row__item-value-secondary'})
            type_tube = for_tube.find_all('div')[-1].text.strip()
            standard = dr.find('div', {'class': 'table-row__item-value-primary'}).text.split(',')
            steel = row[0].text
            diameter = float(row[1].text.split('/')[0].strip())
            wall = float(row[2].text)
            region = row[3].text
            a_r = row[4].find('span').text.split('/')

            try:
                availability = float(a_r[0].strip())
            except ValueError:
                availability = 0

            try:
                if len(a_r) > 1:
                    reserve = float(a_r[-1].strip())
                else:
                    reserve = 0

            except ValueError:
                raise ValueError()

            try:
                price = float(row[5].text.replace(u'\xa0', u'').replace('i', ''))
            except ValueError:
                price = 0

            for s in standard:
                main_list.append({'type_tube': type_tube, 'standard': s.replace('\n', '').strip(), 'steel': steel,
                                  'diameter': diameter, 'wall': wall, 'region': region,
                                  'availability': availability, 'reserve': reserve,
                                  'price': price, 'article': article, 'type_of_length': type_of_length})

        page += 1
        browser.get(new_url + f'?PAGEN_1={page}')

json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('chelpipe2.json', "w",  encoding='utf-8') as file:
    file.write(json_list)
browser.quit()
