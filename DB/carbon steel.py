from DB_api import db


data = ('10', '10-6', '20', '20-3', '35', '45', '45-1', '50', '60', '70')
for d in data:
    db.insert('carbon_steel', 'name', (d,))
