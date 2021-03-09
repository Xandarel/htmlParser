from bs4 import BeautifulSoup
import json
import urllib3
from parsing import get_html


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = 'https://ferrum-trade.ru/shop/'
html = get_html(base_url)
sub_group = list()
soup = BeautifulSoup(html, 'lxml')
div = soup.find_all('div', {"class": "ishop-block"})[1]
li = div.find_all('li')[1:]
for l in li:
    a = l.find_all('a')
    sub_group.append(a[0].get('href'))
main_list = list()

for url in sub_group:
    shop = base_url + url
    category = get_html(shop)
    soup = BeautifulSoup(category, 'lxml')
    product_window = soup.find_all('div', {'class': 'product-window'})
    for pw in product_window:
        info = pw.find_all('a', {'class': 'product-link'})[0].text.split()

        try:
            standard_index = info.index('ГОСТ')
        except ValueError:
            standard_index = 3

        name = ' '.join(info[:standard_index])
        if 'х' in name:
            name = ' '.join(name.split()[:-1])

        if standard_index != 3:
            standard = info[standard_index + 1]
        else:
            if 'ГОСТ' in info[standard_index]:
                standard = info[standard_index].replace('ГОСТ', '')
            else:
                standard = ''

        diameter_wall = info[-2].split('х')

        if len(diameter_wall) == 2:
            diameter = float(diameter_wall[0])
            wall = float(diameter_wall[-1].replace(',', '.'))
        elif len(diameter_wall) == 3:
            diameter = float(diameter_wall[0])
            wall = float(diameter_wall[-1].replace(',', '.'))

        steel = info[-1].replace('(', '').replace(')', '').replace('ст', '')
        price = pw.find('div', {'class': 'set-box'})
        p = price.find('p', {'class': 'mini-price'}).text.split()

        if len(p) == 4:
            price = float(p[2])
        elif len(p) == 2:
            price = float(p[0])
        else:
            price = 0

        main_list.append({'name': name, 'standard': standard, 'diameter': diameter,
                          'wall': wall, 'steel': steel, 'price': price, 'region': 'Иркутск'})
json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
with open('forum_trade.json', "w",  encoding='utf-8') as file:
    file.write(json_list)




