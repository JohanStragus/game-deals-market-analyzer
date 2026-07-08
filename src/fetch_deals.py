from dotenv import load_dotenv
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import os
import json

# Leemos primero las variables del .env
load_dotenv()

# obtenemos la API
api_key = os.getenv("ITAD_API_KEY")

# url donde haremos la petición a la API
base_url = "https://api.isthereanydeal.com/deals/v2"

# Lista para guardar todas las ofertas
all_deals = []

# Variables para controlar las páginas
offset = 0
page = 1

while True:
    # Parámetros de los cuales queremos obtener información de dicha API
    params = {
        "country": "ES",
        "limit": 200,
        "offset": offset,
        "sort": "-cut",
        "nondeals": "false",
        "mature": "false",
        "filter": json.dumps({
            "type": [1]
        })
    }

    # Unificamos la base url y los parametros y los codificamos para que la url lo entienda
    url = base_url + "?" + urlencode(params)

    # preparamos el header
    headers = {
        "ITAD-API-Key": api_key,
        "User-Agent": "GameDealsMarketAnalyzer/1.0"
    }

    # preparamos la request personalizada
    request = Request(url, headers=headers)

    # Hacemos la petición usando with (with cierra automáticamente la conexión al terminar)
    with urlopen(request, timeout=20) as response:
        # Recibimos los datos de la API
        data = response.read().decode("utf-8")

        # Una vez convertido los bits a texto , pasamos el texto Json a objeto de Python
        js = json.loads(data)

    # Obtenemos la lista de ofertas de cada página
    deals = js["list"]

    # Añadimos las ofertas a nuestra variable
    all_deals.extend(deals)

    # Visualizamos por que página vamos y cuantos ofertas tenemos
    print(f"Página: {page} descargada: {len(deals)} ofertas")

    # Comprobamos el total acumulado
    print(f"Total acumulado: {len(all_deals)} ofertas")

    # Si no hay más páginas salimos del bucle
    if not js["hasMore"]:
        break

    # Si hay más páginas actualizamos el offset, es decir, la posición desde donde seguirá leyendo la API
    offset = js["nextOffset"]

    # Vamos realizando la paginación
    page += 1

# Creamos un JSON final con todas las ofertas juntas
js_final = {
    "totalDeals": len(all_deals),
    "list": all_deals
}

# Pasamos los datos al fichero, si dicho fichero no existe lo crea solo, si existe lo sobreescribe
with open("./data/raw/deals_raw.json", "w", encoding="utf-8") as archivo:  
    # usamos dump, que pasa el objeto Python a fichero JSON
    json.dump(js_final, archivo, indent=4, ensure_ascii=False)


# Mensaje temporal para verificar que recibimos bien las cosas
print("Descarga completada.")
print(f"Total de ofertas descargadas: {len(all_deals)}")

