from bs4 import BeautifulSoup
from parsing import get_html
import re

main_list = list()
new_url = 'http://dmk.su/truby-i-otvody-jshop/truby-bolshogo-diametra/truba-820kh14-mm-i-vyshe-l-6m-12m'
# new_url = 'http://dmk.su/truby-i-otvody-jshop/otvody/otvod-st-du-89-kh-3-5-20-120-180'
html = get_html(new_url)
soup = BeautifulSoup(html, 'lxml')
product_div = soup.find('div', {'class': 'tab-cont active'})

# print(product_div)
p = product_div.find_all('p')
if len(p) > 1:
    diameter_wall = re.search(r'[+-]?([0-9]*[.])?[0-9]+х[+-]?([0-9]*[.])?[0-9]+', p[0].text)[0].split('х')
    diameter = diameter_wall[0]
    wall = diameter_wall[-1]
    steel = re.search(r'ст.\d*', p[2].text)[0].replace('ст.', '')
    standard = re.search(r'ГОСТ \d*', p[2].text)[0].replace('ГОСТ ', '')
    print(diameter_wall)
    print(steel)
    print(standard)
    for pp in p:
        print(pp.text)
input()

p_data = product_div.get_text(separator='\n').strip().split('\n')
h1 = soup.find('h1', {'class': '456'}).text.strip().split()

if len(h1) == 6:
    product_type = h1[0] + ' ' + h1[1]
    diameter_wall = re.search(r'[+-]?([0-9]*[.])?[0-9]+х[+-]?([0-9]*[.])?[0-9]+', p[0].text)[0].split('х')
    try:
        diameter = float(diameter_wall[0])
    except:
        diameter = None
    try:
        wall = float(diameter_wall[-1])
    except:
        wall = None
else:
    product_type = h1[0]
    if 'Труба' in product_type:
        try:
            diameter = float(h1[1].split('х')[0])
        except:
            diameter = None
        try:
            wall = float(h1[1].split('х')[-1].replace(',', '.'))
        except:
            wall = None
    else:
        pass
        # continue
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
                      'standard': standard,
                      'steel': steel
                      })
else:
    main_list.append({'region': 'хабаровск',
                      'type': product_type,
                      'diameter': diameter,
                      'wall': wall,
                      'price': price,
                      'max_price': max_price,
                      'min_price': min_price,
                      })

# json_list = json.dumps(main_list,  ensure_ascii=False).replace('},', '},\n')
# with open('dmk2.json', "w",  encoding='utf-8') as file:
#     file.write(json_list)


