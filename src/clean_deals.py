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

# Guardamos los game_id ya procesados para evitar duplicados
game_ids_procesados = set()

# Recorremos los datos
for data in js["list"]:
    # 1. OBTENER, LIMPIAR, TRANSFORMAR LOS DATOS QUE QUEREMOS

    # GAMES
    game_id = data["id"]

    # Si el juego ya se procesó, saltamos este registro duplicado
    if game_id in game_ids_procesados:
        continue

    game_ids_procesados.add(game_id)
    
    slug = data["slug"]
    title = data["title"]
    game_type = data["type"]
    mature = data["mature"]

    # SHOPS
    shop_id = data["deal"]["shop"]["id"]
    shop_name = data["deal"]["shop"]["name"]

    # DEALS
    current_price = data["deal"]["price"]["amount"]
    regular_price = data["deal"]["regular"]["amount"]
    currency = data["deal"]["price"]["currency"]
    discount_cut = data["deal"]["cut"]

    # Campos calculados
    saving_amount = round(regular_price - current_price, 2)
    is_free = current_price == 0
    
    # Estos campos podrían venir como null
    store_low_data = data["deal"].get("storeLow")
    store_low = store_low_data["amount"] if store_low_data else None

    history_low_data = data["deal"].get("historyLow")
    history_low = history_low_data["amount"] if history_low_data else None

    history_low_1y_data = data["deal"].get("historyLow_1y")
    history_low_1y = history_low_1y_data["amount"] if history_low_1y_data else None

    history_low_3m_data = data["deal"].get("historyLow_3m")
    history_low_3m = history_low_3m_data["amount"] if history_low_3m_data else None

    timestamp = data["deal"]["timestamp"]
    expiry = data["deal"].get("expiry")
    url = data["deal"]["url"]

    # Guardamos si es True o False si el precio es menor o igual al historico
    is_historical_low = current_price <= history_low if history_low is not None else None

    # Clasificamos el precio actual por rangos
    if current_price == 0:
        price_range = "Gratis"
    elif current_price < 5:
        price_range = "0,01€ - 4,99€"
    elif current_price < 10:
        price_range = "5€ - 9,99€"
    elif current_price < 20:
        price_range = "10€ - 19,99€"
    elif current_price < 40:
        price_range = "20€ - 39,99€"
    else:
        price_range = "40€ o más"

    # Clasificamos el descuento por rangos
    if discount_cut == 100:
        discount_range = "100%"
    elif discount_cut >= 90:
        discount_range = "90% - 99%"
    elif discount_cut >= 75:
        discount_range = "75% - 89%"
    elif discount_cut >= 50:
        discount_range = "50% - 74%"
    elif discount_cut >= 25:
        discount_range = "25% - 49%"
    else:
        discount_range = "0% - 24%"

    # DRMS
    # Al ser una lista la obtenemos para recorrerla después y si no tiene nada ponemos una lista vacía
    drms = data["deal"].get("drm") or []

    # 2. INSERTAR DATOS LIMPIOS EN SQLITE

    # Games
    cur.execute(""" INSERT OR IGNORE INTO games(game_id, slug, title, type, mature) VALUES(?, ?, ?, ?, ?)""",
                (game_id, slug, title, game_type, mature))
    
    # shops
    cur.execute(""" INSERT OR IGNORE INTO shops(shop_id, shop_name) VALUES(?, ?)""", 
                (shop_id, shop_name))
    
    # deals
    cur.execute(""" INSERT INTO deals (
                                                game_id,
                                                shop_id,
                                                current_price,
                                                regular_price,
                                                currency,
                                                discount_cut,
                                                saving_amount,
                                                store_low,
                                                history_low,
                                                history_low_1y,
                                                history_low_3m,
                                                timestamp,
                                                expiry,
                                                url,
                                                is_free,
                                                is_historical_low,
                                                price_range,
                                                discount_range
                                            ) 
                                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                            (
                                            game_id,
                                            shop_id,
                                            current_price,
                                            regular_price,
                                            currency,
                                            discount_cut,
                                            saving_amount,
                                            store_low,
                                            history_low,
                                            history_low_1y,
                                            history_low_3m,
                                            timestamp,
                                            expiry,
                                            url,
                                            is_free,
                                            is_historical_low,
                                            price_range,
                                            discount_range
                                            ))
    # Obtenemos el ID automático generado para la oferta
    deal_id = cur.lastrowid

    # drms

    # Recorremos la lista
    for drm in drms:
        # Obtenemos los datos
        drm_id = drm["id"]
        drm_name = drm["name"]

        # Lo insertamos en la tabla drms
        cur.execute(""" INSERT OR IGNORE INTO drms(drm_id, drm_name) VALUES(?, ?)
                    """, (drm_id, drm_name))
        
        # Lo insertamos en la relación entre deal y drm
        cur.execute(""" INSERT OR IGNORE INTO deal_drms(deal_id, drm_id) VALUES(?, ?)""",
                    (deal_id, drm_id))
        
# Guardamos todos los cambios y cerramos la conexión
conn.commit()
conn.close()