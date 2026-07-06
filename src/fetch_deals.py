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

# Parámetros de los cuales queremos obtener información de dicha API
params = {
    "country": "ES",
    "limit": 50,
    "offset": 0,
    "sort": "-cut",
    "nondeals": "false",
    "mature": "false"
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

# Hacemos la petición usando with (with sirve para borrar la conexión una vez termine lo identando de adentro)
with urlopen(request, timeout=20) as response:
    # Recibimos los datos de la API
    data = response.read().decode("utf-8")

    # Una vez convertido los bits a texto , pasamos el texto Json a objeto de Python
    js = json.loads(data)

    # Mostramos el json de forma legible
    print(json.dumps(js, indent=4, ensure_ascii=False))