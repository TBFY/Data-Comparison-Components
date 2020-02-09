import time
import os
from elasticsearch import Elasticsearch
from datetime import datetime
import urllib2
import json 
import base64

URL_ELASTICSEARCH = "https://localhost:9220"
es_user = 'sirenadmin'
es_pass = 'password'
es_index = 'tender'
list_of_id = []
list_of_id_void = []


# Establecemos los parametros den entrada en caso de que no se pasen, como en las pruebas
if str(os.environ.get('IDTENDER')) == "None":
	IDTENDER = 'ocds-0c46vo-0001-00057255-55b4-4d67-81bb-3d959b476302_ocds-b5fd17-ac2cf6de-240e-4012-9b4c-17a41903f3e1-black001-dn391433-52516609'
else:
	IDTENDER = str(os.environ.get('LIMITE'))

if str(os.environ.get('LIMITE')) == "None":
	LIMITE = '400'
else:
	LIMITE = str(os.environ.get('LIMITE'))

if str(os.environ.get('TOTAL_DATOS')) == "None":
	TOTAL_DATOS = '10'
else:
	TOTAL_DATOS = str(os.environ.get('TOTAL_DATOS'))




# Habrimos el registro de trazas de los logs
f = open("salida.log", "w")
f.write(" + Inicio del proceso de carga de datos" + "\n")
f.write(" + Variables de Entorno:" + "\n")
f.write("   - ID del Tender a consultar: " + IDTENDER + "\n")
f.write("   - LIMITE del numero de consultas a realizar en search-api: " + LIMITE + "\n")
f.write("   - TOTAL_DATOS para almacenar de tender en elasticsearch: " + LIMITE + "\n")
f.write("   - URL de ElasticSearch: " + URL_ELASTICSEARCH + "\n")
f.write("     - Usuario: ElasticSearch: " + es_user + "\n")
f.write("     - Password: ElasticSearch: " + es_pass + "\n")

es = Elasticsearch(URL_ELASTICSEARCH, http_auth=(es_user,es_pass), verify_certs=False)
res_json = es.cluster.health(wait_for_status='yellow', request_timeout=100)
# https://localhost:9220/_cluster/health?wait_for_status=yellow&timeout=100s

# Borramos el indice si existe
es.indices.delete(index=es_index, ignore=[400, 404])

# Funcion que realiza un busqueda de Tender similares he inserta en elasticsearch los datos
def iteracion (id_tender):
	global list_of_id
	global list_of_id_void
	global TOTAL_DATOS
	global LIMITE
	f.write("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?source=tender&size=" + LIMITE + "\n")
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?size=" + LIMITE)
	response = urllib2.urlopen(req)
	json_data_search_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_search_api:
		if rows['id'] not in list_of_id and rows['id'] not in list_of_id_void and len(list_of_id) <= int(TOTAL_DATOS):
			f.write("+ Analizamos id: " + rows['id'] + "\n")
			print ("+ Analizamos id: " + rows['id'] + " - list_of_id: " + str(len(list_of_id)) + " - list_of_id_void: " + str(len(list_of_id_void)))
			req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + rows['id'])
			try:
				response = urllib2.urlopen(req)
			except:
				f.write("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/tender/" + rows['id'] + "\n")
				f.write(response)
				f.write("\n")
				time.sleep(2)
				break
			json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))	
			if json_data_kg_api.get('id'):
				list_of_id.append(rows['id'])
				f.write ("  - Anadimos el id - Count en list_of_id: " + str(len(list_of_id)) + "\n")
				# Insertar en Elasticsearch
				doc1 = {
					'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
					'id_search': id_tender,
					'id': json_data_kg_api['id'],
					'title': json_data_kg_api['title'],
					'description': json_data_kg_api['description'],
					'status': json_data_kg_api['status']
					}
				res = es.index(index=es_index, body=doc1)
				iteracion(json_data_kg_api['id'])
			else:
				list_of_id_void.append(rows['id'])
				f.write("  - No se ha recuperado datos de kg-api  - Count en list_of_id: " + str(len(list_of_id_void)) + "\n")


##################################
# main
##################################
req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + IDTENDER)
response = urllib2.urlopen(req)
json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
doc1 = {
	'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
	'id_search': "",
	'id': json_data_kg_api['id'],
	'title': json_data_kg_api['title'],
	'description': json_data_kg_api['description'],
	'status': json_data_kg_api['status']
	}
res = es.index(index=es_index, body=doc1)
list_of_id.append(IDTENDER)

iteracion(IDTENDER)
  

f.write("\n")
f.write("Numero de elementos insertados: "+ str(len(list_of_id)) + "\n")
f.write("Numero de elementos omitidos por no tener informacion el kn-api: "+ str(len(list_of_id_void)) + "\n")
f.write("\n")

f.write(" + Fin del proceso de carga de datos" + "\n")

f.close()