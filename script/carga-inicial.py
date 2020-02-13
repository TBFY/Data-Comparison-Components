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
es_index_kg_api_tender = 'tender'
es_index_kg_api_tender_document = 'tender-document'
es_index_kg_api_award = 'award'
es_index_kg_api_award_document = 'award-document'
es_index_kg_api_award_supplier = 'award-supplier'
es_index_search_api = 'search'
list_of_id = []
list_of_id_void = []


# Establecemos los parametros den entrada en caso de que no se pasen, como en las pruebas
if str(os.environ.get('IDTENDER')) == "None":
	IDTENDER = 'ocds-0c46vo-0001-8233113a-28c7-4626-9c41-2f3cbfd7d1e6_ocds-b5fd17-df1f7eb0-89c0-4564-a474-ede9131fc40f-sch---7234'
else:
	IDTENDER = str(os.environ.get('IDTENDER'))

if str(os.environ.get('TOTAL_DATOS_TENDER_SEARCH')) == "None":
	TOTAL_DATOS_TENDER_SEARCH = '100'
else:
	TOTAL_DATOS_TENDER_SEARCH = str(os.environ.get('TOTAL_DATOS_TENDER_SEARCH'))

if str(os.environ.get('TOTAL_DATOS_TENDER')) == "None":
	TOTAL_DATOS_TENDER = '100'
else:
	TOTAL_DATOS_TENDER = str(os.environ.get('TOTAL_DATOS_TENDER'))

if str(os.environ.get('TOTAL_DATOS_AWARD')) == "None":
	TOTAL_DATOS_AWARD = '100'
else:
	TOTAL_DATOS_AWARD = str(os.environ.get('TOTAL_DATOS_AWARD'))


# Habrimos el registro de trazas de los logs
f = open("salida.log", "w")
f.write(" + Inicio del proceso de carga de datos" + "\n")
f.write(" + Variables de Entorno:" + "\n")
f.write("   - ID del Tender a consultar: " + IDTENDER + "\n")
f.write("   - TOTAL_DATOS_TENDER_SEARCH del numero de consultas a realizar en search-api: " + TOTAL_DATOS_TENDER_SEARCH + "\n")
f.write("   - TOTAL_DATOS_TENDER para almacenar de tender en elasticsearch: " + TOTAL_DATOS_TENDER + "\n")
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

# Borramos los datos del indice si existe
es.indices.delete(index=es_index_search_api, ignore=404)
es.indices.delete(index=es_index_kg_api_tender, ignore=404)
es.indices.delete(index=es_index_kg_api_tender_document, ignore=404)
es.indices.delete(index=es_index_kg_api_award, ignore=404)
es.indices.delete(index=es_index_kg_api_award_document, ignore=404)
es.indices.delete(index=es_index_kg_api_award_supplier, ignore=404)



###############################################
###    SEARCH
###############################################
def iteracion_search (id_tender):
	global TOTAL_DATOS_TENDER
	global TOTAL_DATOS_TENDER_SEARCH
	global LIMITE
	if inserta_tender (id_tender):
		f.write("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?source=tender&size=" + TOTAL_DATOS_TENDER_SEARCH + "\n")
		print("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?source=tender&size=" + TOTAL_DATOS_TENDER_SEARCH)
		req = urllib2.Request("http://tbfy.librairy.linkeddata.es/search-api/documents/" + id_tender + "/items?source=tender&size=" + TOTAL_DATOS_TENDER_SEARCH)
		response = urllib2.urlopen(req)
		json_data_search_api = json.loads(response.read().decode('utf8', 'ignore'))
		for rows in json_data_search_api:
			if rows['id'] not in list_of_id and rows['id'] not in list_of_id_void and len(list_of_id) <= int(TOTAL_DATOS_TENDER):
				if inserta_tender (rows['id']):
					insertar_indice_search (id_tender, rows['id'])
	else:
		print ("No se puede recuperar el Tender: " + id_tender + " por lo que no realizamos mas busquedas sobre este Tender")

def insertar_indice_search (id_search, id_result):
	doc = {
		'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
		'id_search': id_search,
		'id': id_result
		}
	while True:
		try:
			res = es.index(index=es_index_search_api, id=id_result, body=doc)
		except:
			print ("---- Fallo al insertar registro en \"" + es_index_search_api + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_search_api + ": " + id_search + " -> " + id_result)
			time.sleep(10)
			continue
		break
	print ("+ " + es_index_search_api + ": " + id_search + " -> " + id_result)
	return True

###############################################
###    AWARD
###############################################
def iteracion_award (total_award):
	global TOTAL_DATOS_AWARD
	f.write("+ Buscamos award: " + "http://tbfy.librairy.linkeddata.es/kg-api/award?size=" + total_award + "\n")
	print("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/kg-api/award?size=" + total_award)
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/award?size=" + total_award)
	response = urllib2.urlopen(req)
	json_data_award_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_award_api:
		inserta_award (rows['id'])

def inserta_award (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/award/" + id)
	try:
		response = urllib2.urlopen(req)
	except:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/award/" + id)
		print("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	if json_data_kg_api.get('id'):
		f.write ("  - Anadimos el id " + id + " award\n")
	else:
		f.write("  - No se ha recuperado datos de kg-api " + id + " award\n")
		return False
	doc = {
		'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
		'id': id,
		'title': json_data_kg_api.get('title'),
		'description': json_data_kg_api.get('description'),
		'date': json_data_kg_api.get('date'),
		'contractPeriodStartDate': json_data_kg_api.get('contractPeriod').get("startDate"),
		'contractPeriodEndDate': json_data_kg_api.get('contractPeriod').get("endDate"),
		'awardValue': json_data_kg_api.get('value').get("amount"),
		'awardCurrency': json_data_kg_api.get('value').get("currency"),
		'tenderId': json_data_kg_api.get('tender').get("id"),
		'status': json_data_kg_api.get('status')
		}
	while True:
		try:
			res = es.index(index=es_index_kg_api_award, id=id, body=doc)
		except:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_award + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_award + ": " + id)
			time.sleep(10)
			continue
		break
	print ("+ " + es_index_kg_api_award + ": " + id)
	inserta_award_document (id)
	inserta_award_supplier (id)
	return True


def inserta_award_document (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/document")
	try:
		response = urllib2.urlopen(req)
	except:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/document\n")
		print(response)
		print("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_kg_api:
		doc = {
			'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
			'id_award_source': id,
			'id': rows.get('id'),
			'type': rows.get('type'),
			'language': rows.get('language'),
			'url': rows.get('url')
			}
		while True:
			try:
				res = es.index(index=es_index_kg_api_award_document, id= rows['id'], body=doc)
			except:
				print ("---- Fallo al insertar registro en \"" + es_index_kg_api_award_document + "\" de ElasticSearch, esperamos 10 segundo")
				print ("---- " + es_index_kg_api_award_document + ": " + id)
				time.sleep(10)
				continue
			break
		print ("+-- " + es_index_kg_api_award_document + ": " + id)
	return True

def inserta_award_supplier (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/supplier")
	try:
		response = urllib2.urlopen(req)
	except:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/supplier")
		print("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_kg_api:
		doc = {
			'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
			'id_award_source': id,
			'id': rows.get('id'),
			'legalname': rows.get('legalname'),
			'jursidiction': rows.get('jursidiction'),
			'street': rows.get('address').get('street'),
			'postalCode': rows.get('address').get('postalCode'),
			'locality': rows.get('address').get('locality'),
			'country': rows.get('address').get('country'),
			'contactName': rows.get('contactPoint').get('name'),
			'contactEmail': rows.get('contactPoint').get('email'),
			'contactTelephone': rows.get('contactPoint').get('telephone'),
			'contactTelephone': rows.get('contactPoint').get('telephone'),
			'contactURL': rows.get('contactPoint').get('URL'),
			'contactFax': rows.get('contactPoint').get('fax')
			}
		while True:
			try:
				res = es.index(index=es_index_kg_api_award_supplier, id=id, body=doc)
			except:
				print ("---- Fallo al insertar registro en \"" + es_index_kg_api_award_supplier + "\" de ElasticSearch, esperamos 10 segundo")
				print ("---- " + es_index_kg_api_award_supplier + ": " + id)
				time.sleep(10)
				continue
			break
		print ("+-- " + es_index_kg_api_award_supplier + ": " + id)
	return True
	
###############################################
###    TENDER
###############################################
def inserta_tender (id):
	global list_of_id
	global list_of_id_void
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id)
	try:
		response = urllib2.urlopen(req)
	except:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id)
		print("")
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
		'id': id,
		'title': json_data_kg_api.get('title'),
		'description': json_data_kg_api.get('description'),
		'awardCriteria': json_data_kg_api.get('award').get('criteria'),
		'awardCriteriaDetails': json_data_kg_api.get('award').get('criteriaDetails'),
		'tenderPeriodStartDate': json_data_kg_api.get('tenderPeriod').get('StartDate'),
		'tenderPeriodEndDate': json_data_kg_api.get('tenderPeriod').get('eEndDate'),
		'minEstimatedValueAmount': json_data_kg_api.get('value').get('minEstimatedAmount'),
		'minEstimatedValueCurrency': json_data_kg_api.get('value').get('minEstimatedCurrency'),
		'maxEstimatedValueAmount': json_data_kg_api.get('value').get('maxEstimatedAmount'),
		'maxEstimatedValueCurrency': json_data_kg_api.get('value').get('maxEstimatedCurrency'),
		'eligibilityCriteria': json_data_kg_api.get('eligibilityCriteria'),
		'status': json_data_kg_api.get('status')
		}
	while True:
		try:
			res = es.index(index=es_index_kg_api_tender, id=id, body=doc)
		except:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_tender + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_tender + ": " + id)
			time.sleep(10)
			continue
		break
	print ("+ " + es_index_kg_api_tender + ": " + id + " - list_of_id: " + str(len(list_of_id)) + " - list_of_id_void: " + str(len(list_of_id_void)))
	inserta_tender_document (id)
	return True

def inserta_tender_document (id):
	global list_of_id
	global list_of_id_void
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id + "/document")
	try:
		response = urllib2.urlopen(req)
	except:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id + "/document")
		print("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_kg_api:
		doc = {
			'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
			'id_tender_source': id,
			'id': rows['id'],
			'type': rows['type'],
			'language': rows['language'],
			'url': rows['url']
			}
		while True:
			try:
				res = es.index(index=es_index_kg_api_tender_document, id= rows['id'], body=doc)
			except:
				print ("---- Fallo al insertar registro en \"" + es_index_kg_api_tender_document + "\" de ElasticSearch, esperamos 10 segundo")
				print ("---- " + es_index_kg_api_tender_document + ": " + id)
				time.sleep(10)
				continue
			break
		print ("+-- " + es_index_kg_api_tender_document + ": " + id)
	return True

        

##################################
# main
##################################

iteracion_search(IDTENDER)

iteracion_award (TOTAL_DATOS_AWARD)

f.write("\n")
f.write("Numero de elementos insertados: "+ str(len(list_of_id)) + "\n")
f.write("Numero de elementos omitidos por no tener informacion el kn-api: "+ str(len(list_of_id_void)) + "\n")
f.write("\n")

f.write(" + Fin del proceso de carga de datos" + "\n")

f.close()
