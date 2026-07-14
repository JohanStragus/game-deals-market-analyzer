import sqlite3
import json

# Creamos la conexión con la base de datos y si no existe crea el archivo
conn = sqlite3.connect("./database/bd_games.sqlite")

# Creamos el cursor para ejecutar instrucciones SQL
cur = conn.cursor()

# comprobación de claves foráneas
cur.execute("PRAGMA foreign_keys = ON")

# Creamos las tablas sqlite
cur.executescript('''
                    CREATE TABLE IF NOT EXISTS games (
                        game_id TEXT PRIMARY KEY,
                        slug TEXT,
                        title TEXT NOT NULL,
                        type TEXT,
                        mature BOOLEAN
                );
                    
                    CREATE TABLE IF NOT EXISTS shops (
                        shop_id INTEGER PRIMARY KEY,
                        shop_name TEXT NOT NULL
                );
                
                    CREATE TABLE IF NOT EXISTS deals (
                        deal_id INTEGER PRIMARY KEY,
                        game_id TEXT NOT NULL REFERENCES games(game_id),
                        shop_id INTEGER NOT NULL REFERENCES shops(shop_id),
                        current_price REAL,
                        regular_price REAL,
                        currency TEXT,
                        discount_cut INTEGER,
                        saving_amount REAL,
                        store_low REAL,
                        history_low REAL,
                        history_low_1y REAL,
                        history_low_3m REAL,
                        timestamp TEXT,
                        expiry TEXT,
                        url TEXT,
                        is_free BOOLEAN,
                        is_historical_low BOOLEAN,
                        price_range TEXT,
                        discount_range TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS drms (
                        drm_id INTEGER PRIMARY KEY,
                        drm_name TEXT NOT NULL
                    );
                    
                    CREATE TABLE IF NOT EXISTS deal_drms (
                        deal_id INTEGER NOT NULL REFERENCES deals(deal_id),
                        drm_id INTEGER NOT NULL REFERENCES drms(drm_id),
                        PRIMARY KEY(deal_id, drm_id)
                    );
                    
''')

# Eliminar los datos de las tablas cada vez que ejecutamos, así evitamos duplicaciones
cur.execute("DELETE FROM deal_drms")
cur.execute("DELETE FROM deals")
cur.execute("DELETE FROM drms")
cur.execute("DELETE FROM shops")
cur.execute("DELETE FROM games")

# Abrimos el archivo con los datos
with open("./data/raw/deals_raw.json", "r", encoding="utf-8") as file:
    # Obtenemos los datos del archivo JSON y lo convertimos en un objeto Python
    js = json.load(file)

# Recorremos los datos
for data in js["list"]:
    # Obtenemos los datos que queremos
    game_id = data["id"] # TEXT

