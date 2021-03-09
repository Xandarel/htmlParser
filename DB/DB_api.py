import sqlite3


class SqliteDB:
    def __init__(self):
        self.path = r'front/db_test6.sqlite'
        self.con = self._get_connection()
        self.cur = self.con.cursor()
        self.carbon = self._get_carbon()

    def _get_carbon(self):
        ans = list()
        try:
            for c in self.select('name', 'carbon_steel', mode=0):
                ans.append(c[0])
            return ans
        except sqlite3.OperationalError:
            return 0

    def select(self, table_element, table_name, where='', values=(), mod='', mode=1):
        request = f' SELECT {mod} {table_element} FROM {table_name} {where}'
        self.cur.execute(request, values)

        if mode == 1:
            return self.cur.fetchone()
        elif mode == 0:
            return self.cur.fetchall()
        else:
            return self.cur

    def insert(self, table_name, columns, values):
        if len(values) == 1:
            val = '? '
        else:
            val = '?, '
        request = f' INSERT INTO {table_name} ({columns}) VALUES ({(val * len(values))})'
        request = request.replace(', )', ')')
        self.cur.execute(request, values)
        self.con.commit()

    def _get_connection(self):
        with sqlite3.connect(self.path) as connection:
            return connection

    def create_table(self, script):
        self.cur.executescript(script)
        if self.carbon:
            self._insert_carbon()
            self.carbon = self._get_carbon()

    def _insert_carbon(self):
        data = ('10', '10-6', '20', '20-3', '35', '45', '45-1', '50', '60', '70')
        for d in data:
            db.insert('carbon_steel', 'name', (d,))


db = SqliteDB()
