from DB_api import db

db.create_table(""" 
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS city (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS steels(
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            steel   TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS company (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS production_method (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            method  TEXT
        );
        
        CREATE TABLE IF NOT EXISTS MinValue (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            standard        TEXT NOT NULL,
            diameter_min    INTEGER NOT NULL,
            diameter_max    INTEGER NOT NULL,
            steel           TEXT NOT NULL,
            wall_min        REAL NOT NULL,
            wall_max        REAL NOT NULL,
            city_id         INTEGER NOT NULL,
            price           INTEGER NOT NULL,
            date_begin      INTEGER NOT NULL,
            date_end        INTEGER,
            FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS articles (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            article INTEGER NOT NULL,
            kis     INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS company_price (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            company_id  INTEGER NOT NULL,
            standard    TEXT,
            steel_id    INTEGER,
            wall        REAL,
            diameter    REAL,
            city_id     INTEGER,
            price_min   INTEGER NOT NULL,
            price_max   INTEGER,
            article_id  INTEGER,
            parce_date  INTEGER NOT NULL,
            url         TEXT,
            method_id   INTEGER,
            file_index  INTEGER,
            FOREIGN KEY (steel_id) REFERENCES steels(id),
            FOREIGN KEY (method_id) REFERENCES  production_method(id), 
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (company_id) REFERENCES company(id),
            FOREIGN KEY (city_id) REFERENCES city(id)
        );
        
        CREATE TABLE IF NOT EXISTS chelpipe (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            standard        TEXT NOT NULL,
            steel_id        INTEGER,
            diameter        REAL,
            wall            REAL,
            city_id         INTEGER,
            price_min       INTEGER NOT NULL,
            price_max       INTEGER,
            article_id      INTEGER NOT NULL,
            parse_date      INTEGER NOT NULL,
            method_id       INTEGER,
            FOREIGN KEY (steel_id) REFERENCES steels(id),
            FOREIGN KEY (method_id) REFERENCES  production_method(id), 
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (city_id) REFERENCES city(id)
        );
        
         CREATE TABLE IF NOT EXISTS carbon_steel (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL
         )
    """)
