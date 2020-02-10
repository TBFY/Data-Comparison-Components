import time
import os
from elasticsearch import Elasticsearch
from datetime import datetime
import urllib2
import json 
import base64
import ssl

URL_ELASTICSEARCH = "https://localhost:9220"
es_user = 'sirenadmin'
es_pass = 'password'
es_index_kg_api = 'tender'
es_index_search_api = 'search'
list_of_id = []
list_of_id_void = []


# Establecemos los parametros den entrada en caso de que no se pasen, como en las pruebas
if str(os.environ.get('IDTENDER')) == "None":
	IDTENDER = 'ocds-0c46vo-0001-8233113a-28c7-4626-9c41-2f3cbfd7d1e6_ocds-b5fd17-df1f7eb0-89c0-4564-a474-ede9131fc40f-sch---7234'
else:
	IDTENDER = str(os.environ.get('IDTENDER'))

if str(os.environ.get('TOTAL_DATOS_SEARCH')) == "None":
	TOTAL_DATOS_SEARCH = '500'
else:
	TOTAL_DATOS_SEARCH = str(os.environ.get('TOTAL_DATOS_SEARCH'))

if str(os.environ.get('TOTAL_DATOS')) == "None":
	TOTAL_DATOS = '100'
else:
	TOTAL_DATOS = str(os.environ.get('TOTAL_DATOS'))




# Habrimos el registro de trazas de los logs
f = open("salida.log", "w")
f.write(" + Inicio del proceso de carga de datos" + "\n")
f.write(" + Variables de Entorno:" + "\n")
f.write("   - ID del Tender a consultar: " + IDTENDER + "\n")
f.write("   - TOTAL_DATOS_SEARCH del numero de consultas a realizar en search-api: " + TOTAL_DATOS_SEARCH + "\n")
f.write("   - TOTAL_DATOS para almacenar de tender en elasticsearch: " + TOTAL_DATOS + "\n")
f.write("   - URL de ElasticSearch: " + URL_ELASTICSEARCH + "\n")
f.write("     - Usuario: ElasticSearch: " + es_user + "\n")
f.write("     - Password: ElasticSearch: " + es_pass + "\n")

es = Elasticsearch(URL_ELASTICSEARCH, http_auth=(es_user,es_pass), ca_certs=False, verify_certs=False, ssl_show_warn=False)

while True:
	try:
		res_json = es.cluster.health(wait_for_status='yellow', request_timeout=10)
	except:
		print ("---- Elastecsearch no esta respondiendo, esperamos 10 segundos")
		time.sleep(10)
		continue
	print("---- Elasticsearch OK")
	break

# Borramos el indice si existe
es.indices.delete(index=es_index_kg_api, ignore=[400, 404])
es.indices.delete(index=es_index_search_api, ignore=[400, 404])


# Funcion que realiza un busqueda de Tender similares he inserta en elasticsearch los datos
def iteracion (id_tender):
	global TOTAL_DATOS
	global TOTAL_DATOS_SEARCH
	global LIMITE
	if inserta_tender (id_tender):
		f.write("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?source=tender&size=" + TOTAL_DATOS_SEARCH + "\n")
		req = urllib2.Request("http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?source=tender&size=" + TOTAL_DATOS_SEARCH)
		response = urllib2.urlopen(req)
		json_data_search_api = json.loads(response.read().decode('utf8', 'ignore'))
		for rows in json_data_search_api:
			if rows['id'] not in list_of_id and rows['id'] not in list_of_id_void and len(list_of_id) <= int(TOTAL_DATOS):
				insertar_indice_search (id_tender, rows['id'])
				inserta_tender (rows['id'])
	else:
		print ("No se puede recuperar el Tender: " + id_tender + " por lo que no realizamos mas busquedas sobre este Tender")



def insertar_indice_search (id_search, id_result):
	doc = {
		'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
		'id_search': id_search,
		'id_result': id_result
		}
	while True:
		try:
			res = es.index(index=es_index_search_api, body=doc)
		except:
			print ("---- Fallo al insertar registro en \"" + es_index_search_api + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_search_api + ": " + id_search + " -> " + id_result)
			time.sleep(10)
			continue
		break
	print ("+ " + es_index_search_api + ": " + id_search + " -> " + id_result)
	return True
	

# Funcion que consulta a KN-API un id y lo inserta en ElasticSearch
def inserta_tender (id):
	global list_of_id
	global list_of_id_void
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id)
	try:
		response = urllib2.urlopen(req)
	except:
		f.write("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id + "\n")
		f.write(response)
		f.write("\n")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	if json_data_kg_api.get('id'):
		list_of_id.append(id)
		f.write ("  - Anadimos el id - Count en list_of_id: " + str(len(list_of_id)) + "\n")
	else:
		list_of_id_void.append(id)
		f.write("  - No se ha recuperado datos de kg-api  - Count en list_of_id: " + str(len(list_of_id_void)) + "\n")
		return False
	doc = {
		'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
		'id': json_data_kg_api['id'],
		'title': json_data_kg_api['title'],
		'description': json_data_kg_api['description'],
		'status': json_data_kg_api['status']
		}
	while True:
		try:
			res = es.index(index=es_index_kg_api, body=doc)
		except:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api + ": " + id)
			time.sleep(10)
			continue
		break
	print ("+ " + es_index_kg_api + ": " + id + " - list_of_id: " + str(len(list_of_id)) + " - list_of_id_void: " + str(len(list_of_id_void)))
	return True
        

##################################
# main
##################################

iteracion(IDTENDER)


f.write("\n")
f.write("Numero de elementos insertados: "+ str(len(list_of_id)) + "\n")
f.write("Numero de elementos omitidos por no tener informacion el kn-api: "+ str(len(list_of_id_void)) + "\n")
f.write("\n")

f.write(" + Fin del proceso de carga de datos" + "\n")

f.close()
