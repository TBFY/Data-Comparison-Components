import time
import os
from elasticsearch import Elasticsearch
from datetime import datetime
import urllib.request, json 

URL_ELASTICSEARCH = "https://localhost:9220"
es_user = 'sirenadmin'
es_pass = 'password'
es_index = 'tender'

# IDTENDER = "ocds-0c46vo-0009-DN379620-1_DN379620-1"
# LIMITE = "10"

# Habrimos el registro de trazas de los logs
f = open("salida.log", "w")
f.write(" + Inicio del proceso de carga de datos" + "\n")
f.write(" + Variables de Entorno:" + "\n")
f.write("   - ID del Tender a consultar: " + str(os.environ.get('IDTENDER')) + "\n")
f.write("   - LIMITE del numero de consultas a realizar: " + str(os.environ.get('LIMITE')) + "\n")
f.write("   - URL de ElasticSearch: " + URL_ELASTICSEARCH + "\n")
f.write("     - Usuario: ElasticSearch: " + es_user + "\n")
f.write("     - Password: ElasticSearch: " + es_pass + "\n")

# Creamos la conexion con el ElasticSearch de Siren
#es = Elasticsearch(URL_ELASTICSEARCH, http_auth=(es_user,es_pass), verify_certs=False)

# Borramos el indice si existe
#es.indices.delete(index=es_index, ignore=[400, 404])

#with urllib.request.urlopen("http://tbfy.librairy.linkeddata.es/search-api/documents/" + IDTENDER + "/items?size=" + LIMITE) as url_search:
#  json_data_search_api = json.loads(url_search.read().decode())
#
#for rows in json_data_search_api:
#  print("Recorremos id: " + rows['id'])
#  with urllib.request.urlopen("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + rows['id']) as url_kg:
#    json_data_search_api = json.loads(url_kg.read().decode())

  


#doc1 = {
#	'oid': '234243',
#	'tender': 'Uno',
#	'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
#	}
#
## res = es.index(index=es_index, doc_type='id', id=1, body=doc1)
#
#res = es.index(index=es_index, body=doc1)
#print(res['result'])



# wait for yellow status
#for _ in range(1 if nowait else 100):
#    try:
#        client.cluster.health(wait_for_status='yellow')
#    except ConnectionError:
#        time.sleep(.1)
#else:
#    # timeout
#    raise SkipTest("Elasticsearch failed to start.")
		


f.write(" + Fin del proceso de carga de datos" + "\n")

f.close()