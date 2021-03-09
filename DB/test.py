import datetime
import json
from tqdm import tqdm
from DB_api import db

with open("../metallservice_chelyabinsk.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)
for i in tqdm(range(len(data))):
    if data[i]['name'] == "Трубы нерж. ЭСВ 18х1.5 имп зерк." \
            and data[i]['type'] == "нерж. ЭСВ" \
            and data[i]["wall"] == "1.5" \
            and data[i]["diameter"] == 18.0 \
            and data[i]["steel"] == "AISI 201" \
            and data[i]["region"] == "Курск" \
            and data[i]["price_min"] == "84" \
            and data[i]["price_max"] == "85" \
            and data[i]["url"] == "https://mc.ru/region/kursk/metalloprokat/truby_nerzhaveyushchie_ehlektrosvarnye_a":
        print(f'\n{i}')
        break
