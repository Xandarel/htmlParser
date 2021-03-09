from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import psutil
import urllib3
from parsing import get_html


start_time = datetime.now()

urllib3.disable_warnings()
base_url = 'https://market.chelpipe.ru/'
base_html = get_html(base_url)

main_list = list()
a = 'production/truby-besshovnye/'
page = 1
new_url = (base_url + a)
new_url_html = get_html(new_url)
soup = BeautifulSoup(new_url_html, 'lxml')
while True:
    try:
        table_soup = soup.find('div', {'class': 'table__main'})
        print(page)
    except:
        break
    if not table_soup:
        break
    div_row = table_soup.find_all('div', {'class': 'table-row'})
    for dr in div_row:

        page_product = dr.find('a').get('href')
        product = BeautifulSoup(get_html(base_url+page_product[1:]), 'lxml')
        cart = product.find('div', {'class': 'product-card-main__stats'})
        data = cart.find_all('div', {'class': 'product-card-main__stats-item-value'})

        production_method = data[5].text
        if production_method == 'Горячедеформированные трубы':
          production_method = 'г/д'
        elif production_method == 'Холоднодеформированные трубы':
          production_method = 'х/д'
        elif production_method == 'Электросварные трубы':
          production_method = 'ЭСВ'
        else:
          production_method = None
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

        float_prices = []
        if 'от' in row[5].text:
          price_table = product.find('div', {'class': "new-table__inner"})
          price_table = price_table.find_all('div', {'class': 'new-table__row'})[1]
          prices = price_table.find_all('div', {'class': 'new-table__cell--order-1'})
          for pr in prices:
            buff_price = pr.find('div', {'class': 'new-table__cell-value'}).text.replace(u'\xa0', u'').replace('руб', '').strip()
            if buff_price == '—':
              float_prices.append(0)
            else:
              float_prices.append(float(buff_price))
        else:
          try:
              price = float(row[5].text.replace(u'\xa0', u'').replace('i', '').replace('от', '').replace('руб.', '').strip())
          except ValueError:
              price = 0

        for s in standard:
            main_list.append({'type_tube': type_tube,
                              'standard': s.replace('\n', '').strip(),
                              'steel': steel,
                              'diameter': diameter,
                              'wall': wall,
                              'region': region,
                              'availability': availability,
                              'reserve': reserve,
                              'price_min': float_prices[0] if float_prices else price,
                              'price_max': float_prices[-1] if float_prices else None,
                              'article': article,
                              'type_of_length': type_of_length,
                              'production_method': production_method})
    page += 1
    soup = BeautifulSoup(get_html(new_url + f'?PAGEN_1={page}'), 'lxml')

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  # memory use in GB...I think
print('memory use:', memoryUse)
end_time = datetime.now()
print(f'Duration: {end_time - start_time}')

json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('truby-besshovnye.json', "w",  encoding='utf-8') as file:
    file.write(json_list)
