import time
import os
from elasticsearch import Elasticsearch
import elasticsearch
from datetime import datetime
from dateutil.parser import parse
import urllib2
import json 
import base64
import ssl

URL_ELASTICSEARCH = "https://localhost:9220"
# URL_ELASTICSEARCH = "https://elastsiren.oesia.com"
es_user = 'sirenadmin'
es_pass = 'password'
es_index_kg_api_tender = 'tender'
es_index_kg_api_tender_document = 'tender-document'
es_index_kg_api_award = 'award'
es_index_kg_api_award_document = 'award-document'
es_index_kg_api_award_supplier = 'award-supplier'
es_index_kg_api_contractingProcess = 'contracting-process'
es_index_kg_api_contractingProcess_tender = 'contracting-process-tender'
es_index_kg_api_contractingProcess_award = 'contracting-process-award'
es_index_search_api = 'search'
list_of_id = []
list_of_id_void = []


# Establecemos los parametros den entrada en caso de que no se pasen, como en las pruebas
if str(os.environ.get('IDTENDER_SEARCH')) == "None":
	IDTENDER_SEARCH = 'ocds-0c46vo-0001-8233113a-28c7-4626-9c41-2f3cbfd7d1e6_ocds-b5fd17-df1f7eb0-89c0-4564-a474-ede9131fc40f-sch---7234'
else:
	IDTENDER_SEARCH = str(os.environ.get('IDTENDER_SEARCH'))

if str(os.environ.get('TOTAL_DATOS_TENDER_SEARCH')) == "None":
	TOTAL_DATOS_TENDER_SEARCH = '20'
else:
	TOTAL_DATOS_TENDER_SEARCH = str(os.environ.get('TOTAL_DATOS_TENDER_SEARCH'))

if str(os.environ.get('TOTAL_DATOS_TENDER')) == "None":
	TOTAL_DATOS_TENDER = '200'
else:
	TOTAL_DATOS_TENDER = str(os.environ.get('TOTAL_DATOS_TENDER'))

if str(os.environ.get('TOTAL_DATOS_AWARD')) == "None":
	TOTAL_DATOS_AWARD = '200'
else:
	TOTAL_DATOS_AWARD = str(os.environ.get('TOTAL_DATOS_AWARD'))

if str(os.environ.get('TOTAL_DATOS_CONTRACTING_PROCESS')) == "None":
	TOTAL_DATOS_CONTRACTING_PROCESS = '200'
else:
	TOTAL_DATOS_CONTRACTING_PROCESS = str(os.environ.get('TOTAL_DATOS_CONTRACTING_PROCESS'))

# Habrimos el registro de trazas de los logs
f = open("salida.log", "w")
f.write(" + Inicio del proceso de carga de datos" + "\n")
f.write(" + Variables de Entorno:" + "\n")
f.write("   - ID del Tender a consultar: " + IDTENDER_SEARCH + "\n")
f.write("   - TOTAL_DATOS_TENDER_SEARCH del numero de consultas a realizar en search-api: " + TOTAL_DATOS_TENDER_SEARCH + "\n")
f.write("   - TOTAL_DATOS_TENDER para almacenar de tender en elasticsearch: " + TOTAL_DATOS_TENDER + "\n")
f.write("   - URL de ElasticSearch: " + URL_ELASTICSEARCH + "\n")
f.write("     - Usuario: ElasticSearch: " + es_user + "\n")
f.write("     - Password: ElasticSearch: " + es_pass + "\n")

es = Elasticsearch(URL_ELASTICSEARCH, http_auth=(es_user,es_pass), ca_certs=False, verify_certs=False, ssl_show_warn=False)

# Inicializamos la conexion con ElasticSearch
while True:
	try:
		res_json = es.cluster.health(wait_for_status='yellow', request_timeout=10)
	except:
		print ("---- Elastecsearch no esta respondiendo, esperamos 10 segundos")
		time.sleep(10)
		continue
	print("---- Elasticsearch OK")
	break

# Realizamos una prueba de escritura en un indice
es.indices.delete(index="borrar", ignore=404)
doc = {'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
while True:
	try:
		res = es.index(index="borrar", body=doc)
	except elasticsearch.ElasticsearchException as es1:
		print ("---- Fallo al insertar registro en el indice temporal de ElasticSearch, esperamos 10 segundo")
		print ("Excepcion: " + str(es1))
		time.sleep(10)
		continue
	break
es.indices.delete(index="borrar", ignore=404)

# Borramos los datos del indice si existe
es.indices.delete(index=es_index_search_api, ignore=404)
es.indices.delete(index=es_index_kg_api_tender, ignore=404)
es.indices.delete(index=es_index_kg_api_tender_document, ignore=404)
es.indices.delete(index=es_index_kg_api_award, ignore=404)
es.indices.delete(index=es_index_kg_api_award_document, ignore=404)
es.indices.delete(index=es_index_kg_api_award_supplier, ignore=404)
es.indices.delete(index=es_index_kg_api_contractingProcess, ignore=404)
es.indices.delete(index=es_index_kg_api_contractingProcess_award, ignore=404)
es.indices.delete(index=es_index_kg_api_contractingProcess_tender, ignore=404)


def convierte_fecha (fecha_texto):
	fecha_time = parse(fecha_texto)
	fecha_time = parse(fecha_texto)
	return fecha_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

###############################################
###    SEARCH
###############################################
def iteracion_search (id_tender):
	global TOTAL_DATOS_TENDER
	global TOTAL_DATOS_TENDER_SEARCH
	global LIMITE
	if inserta_tender (id_tender):
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
	try:
		res = es.index(index=es_index_search_api, id=id_result, body=doc)
	except elasticsearch.ElasticsearchException as es1:
		print ("---- Fallo al insertar registro en \"" + es_index_search_api + "\" de ElasticSearch, esperamos 10 segundo")
		print ("---- " + es_index_search_api + ": " + id_search + " -> " + id_result)
		print ("doc: " + str(doc))
		print ("Excepcion: " + str(es1))
		time.sleep(10)
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
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/award/" + id)
		print(response_error)
		print ("")
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
		'date': convierte_fecha(json_data_kg_api.get('date')),
		'status': json_data_kg_api.get('status')
		}
	if json_data_kg_api.get('contractPeriod'):
		doc['contractPeriodStartDate'] = convierte_fecha(json_data_kg_api.get('contractPeriod').get("startDate"))
		doc['contractPeriodEndDate'] = convierte_fecha(json_data_kg_api.get('contractPeriod').get("endDate"))
	else:
		doc['contractPeriodStartDate'] = None
		doc['contractPeriodEndDate'] = None
	
	if json_data_kg_api.get('value'):
		if json_data_kg_api.get('value').get("amount"):
			doc['awardValue'] = float(json_data_kg_api.get('value').get("amount"))
			doc['awardCurrency'] = json_data_kg_api.get('value').get("currency")
	else:
		doc['awardValue'] = None
		doc['awardCurrency'] = None
	
	if json_data_kg_api.get('tender'):
		doc['tenderId'] = json_data_kg_api.get('tender').get("id")
	else:
		doc['tenderId'] = None
	try:
		res = es.index(index=es_index_kg_api_award, id=id, body=doc)
	except elasticsearch.ElasticsearchException as es1:
		print ("---- Fallo al insertar registro en \"" + es_index_kg_api_award + "\" de ElasticSearch, esperamos 10 segundo")
		print ("---- " + es_index_kg_api_award + ": " + id)
		print ("doc: " + str(doc))
		print ("Excepcion: " + str(es1))
		time.sleep(10)
	print ("+ " + es_index_kg_api_award + ": " + id)
	inserta_award_document (id)
	inserta_award_supplier (id)
	return True


def inserta_award_document (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/document")
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/document\n")
		print(response_error)
		print ("")
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
		try:
			res = es.index(index=es_index_kg_api_award_document, id= rows['id'], body=doc)
		except elasticsearch.ElasticsearchException as es1:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_award_document + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_award_document + ": " + id)
			print ("doc: " + str(doc))
			print ("Excepcion: " + str(es1))
			time.sleep(10)
		print ("+-- " + es_index_kg_api_award_document + ": " + id)
	return True

def inserta_award_supplier (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/supplier")
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/award/" + id + "/supplier")
		print(response_error)
		print ("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_kg_api:
		doc = {
			'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
			'id_award_source': id,
			'id': rows.get('id'),
			'legalname': rows.get('legalname'),
			'jursidiction': rows.get('jursidiction')
			}

		if rows.get('contactPoint'):
			doc['contactName'] = rows.get('contactPoint').get('name')
			doc['contactEmail'] = rows.get('contactPoint').get('email')
			doc['contactTelephone'] = rows.get('contactPoint').get('telephone')
			doc['contactURL'] = rows.get('contactPoint').get('URL')
			doc['contactFax'] = rows.get('contactPoint').get('fax')
		else:
			doc['contactName'] = None
			doc['contactEmail'] = None
			doc['contactTelephone'] = None
			doc['contactURL'] = None
			doc['contactFax'] = None

		if rows.get('address'):
			doc['street'] = rows.get('address').get('street')
			doc['postalCode'] = rows.get('address').get('postalCode')
			doc['locality'] = rows.get('address').get('locality')
			doc['country'] = rows.get('address').get('country')
		else:
			doc['street'] = None
			doc['postalCode'] = None
			doc['locality'] = None
			doc['country'] = None

		try:
			res = es.index(index=es_index_kg_api_award_supplier, id=id, body=doc)
		except elasticsearch.ElasticsearchException as es1:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_award_supplier + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_award_supplier + ": " + id)
			print ("doc: " + str(doc))
			print ("Excepcion: " + str(es1))
			time.sleep(10)
		print ("+-- " + es_index_kg_api_award_supplier + ": " + id)
	return True
	
	
	
	
	
###############################################
###    CONTRACTING PROCESS
###############################################
def iteracion_contracting_process (total_contracting_process):
	global TOTAL_DATOS_CONTRACTING_PROCESS
	f.write("+ Buscamos award: " + "http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess?size=" + total_contracting_process + "\n")
	print("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess?size=" + total_contracting_process)
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess?size=" + total_contracting_process)
	response = urllib2.urlopen(req)
	json_data_total_contracting_process_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_total_contracting_process_api:
		inserta_contracting_process (rows['id'])

def inserta_contracting_process (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess/" + id)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess/" + id)
		print(response_error)
		print ("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	if json_data_kg_api.get('id'):
		f.write ("  - Anadimos el id " + id + " contractingProcess\n")
	else:
		f.write("  - No se ha recuperado datos de kg-api " + id + " contractingProcess\n")
		return False
	doc = {
		'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
		'id': id,
		}
	if json_data_kg_api.get('plan'):
		if json_data_kg_api.get('document'):
			doc['documentId'] = json_data_kg_api.get('plan').get('document').get('id')
			doc['documentType'] = json_data_kg_api.get('plan').get('document').get('tenderNotice')
			doc['documentLanguage'] = json_data_kg_api.get('plan').get('document').get('language')
			doc['documentURL'] =  json_data_kg_api.get('plan').get('document').get('URL')
		else:
			doc['documentId'] = None
			doc['documentType'] = None
			doc['documentLanguage'] = None
			doc['documentURL'] =  None

	try:
		res = es.index(index=es_index_kg_api_contractingProcess, id=id, body=doc)
	except elasticsearch.ElasticsearchException as es1:
		print ("---- Fallo al insertar registro en \"" + es_index_kg_api_contractingProcess + "\" de ElasticSearch, esperamos 10 segundo")
		print ("---- " + es_index_kg_api_contractingProcess + ": " + id)
		print ("doc: " + str(doc))
		print ("Excepcion: " + str(es1))
		time.sleep(10)
	print ("+ " + es_index_kg_api_contractingProcess + ": " + id)
	inserta_contracting_process_tender (id)
	inserta_contracting_process_award (id)
	return True


def inserta_contracting_process_tender (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess/" + id + "/tender")
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess/" + id + "/tender\n")
		print(response_error)
		print ("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_kg_api:
		doc = {
			'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
			'id_contractingProcess_source': id,
			'id': rows.get('id'),
			}
		try:
			res = es.index(index=es_index_kg_api_contractingProcess_tender, id=rows['id'], body=doc)
		except elasticsearch.ElasticsearchException as es1:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_contractingProcess_tender + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_contractingProcess_tender + ": " + id)
			print ("doc: " + str(doc))
			print ("Excepcion: " + str(es1))
			time.sleep(10)
		print ("+-- " + es_index_kg_api_contractingProcess_tender + ": " + id + " --> " + rows['id'])
		inserta_tender(rows['id'])
	return True


def inserta_contracting_process_award (id):
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess/" + id + "/award")
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/contractingProcess/" + id + "/award\n")
		print(response_error)
		print ("")
		time.sleep(2)
		return False
	json_data_kg_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_kg_api:
		doc = {
			'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
			'id_contractingProcess_source': id,
			'id': rows.get('id'),
			}
		try:
			res = es.index(index=es_index_kg_api_contractingProcess_tender, id=rows['id'], body=doc)
		except elasticsearch.ElasticsearchException as es1:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_contractingProcess_award + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_contractingProcess_award + ": " + id)
			print ("doc: " + str(doc))
			print ("Excepcion: " + str(es1))
			time.sleep(10)
		print ("+-- " + es_index_kg_api_contractingProcess_award + ": " + id + " --> " + rows['id'])
		inserta_award(rows['id'])
	return True	
	
	
	
	
###############################################
###    TENDER
###############################################
def iteracion_tender (total_tender):
	global TOTAL_DATOS_TENDER
	f.write("+ Buscamos award: " + "http://tbfy.librairy.linkeddata.es/kg-api/tender?size=" + total_tender + "\n")
	print("+ Buscamos similares: " + "http://tbfy.librairy.linkeddata.es/kg-api/award?size=" + total_tender)
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender?size=" + total_tender)
	response = urllib2.urlopen(req)
	json_data_tender_api = json.loads(response.read().decode('utf8', 'ignore'))
	for rows in json_data_tender_api:
		if len(list_of_id) <= TOTAL_DATOS_TENDER:
			inserta_tender (rows['id'])

def inserta_tender (id):
	global list_of_id
	global list_of_id_void
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id)
		print(response_error)
		print ("")
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
		'eligibilityCriteria': json_data_kg_api.get('eligibilityCriteria'),
		'status': json_data_kg_api.get('status')
		}

	if json_data_kg_api.get('value'):
		if json_data_kg_api.get('value').get('minEstimatedAmount'):
			doc['minEstimatedValueAmount'] = float(json_data_kg_api.get('value').get('minEstimatedAmount'))
			doc['minEstimatedValueCurrency'] = json_data_kg_api.get('value').get('minEstimatedCurrency')
		if json_data_kg_api.get('value').get('maxEstimatedAmount'):
			doc['maxEstimatedValueAmount'] = float(json_data_kg_api.get('value').get('maxEstimatedAmount'))
			doc['maxEstimatedValueCurrency'] = json_data_kg_api.get('value').get('maxEstimatedCurrency')
	else:
		doc['minEstimatedValueAmount'] = None
		doc['minEstimatedValueCurrency'] = None
		doc['maxEstimatedValueAmount'] = None
		doc['maxEstimatedValueCurrency'] = None

	if json_data_kg_api.get('tenderPeriod'):
		doc['tenderPeriodStartDate'] = convierte_fecha(json_data_kg_api.get('tenderPeriod').get('StartDate'))
		doc['tenderPeriodEndDate'] = convierte_fecha(json_data_kg_api.get('tenderPeriod').get('eEndDate'))
	else:
		doc['tenderPeriodStartDate'] = None
		doc['tenderPeriodEndDate'] = None
	
	if json_data_kg_api.get('award'):
		doc['awardCriteria'] = json_data_kg_api.get('award').get('criteria')
		doc['awardCriteriaDetails'] = json_data_kg_api.get('award').get('criteriaDetails')
	else:
		doc['awardCriteria'] = None
		doc['awardCriteriaDetails'] = None
	try:
		res = es.index(index=es_index_kg_api_tender, id=id, body=doc)
	except elasticsearch.ElasticsearchException as es1:
		print ("---- Fallo al insertar registro en \"" + es_index_kg_api_tender + "\" de ElasticSearch, esperamos 10 segundo")
		print ("---- " + es_index_kg_api_tender + ": " + id)
		print ("doc: " + str(doc))
		print ("Excepcion: " + str(es1))
		time.sleep(10)
	print ("+ " + es_index_kg_api_tender + ": " + id + " - list_of_id: " + str(len(list_of_id)) + " - list_of_id_void: " + str(len(list_of_id_void)))
	inserta_tender_document (id)
	return True

def inserta_tender_document (id):
	global list_of_id
	global list_of_id_void
	req = urllib2.Request("http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id + "/document")
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response_error:
		print("Error en la llamada - " + "http://tbfy.librairy.linkeddata.es/kg-api/tender/" + id + "/document")
		print(response_error)
		print ("")
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
		try:
			res = es.index(index=es_index_kg_api_tender_document, id= rows['id'], body=doc)
		except elasticsearch.ElasticsearchException as es1:
			print ("---- Fallo al insertar registro en \"" + es_index_kg_api_tender_document + "\" de ElasticSearch, esperamos 10 segundo")
			print ("---- " + es_index_kg_api_tender_document + ": " + id)
			print ("doc: " + str(doc))
			print ("Excepcion: " + str(es1))
			time.sleep(10)
		print ("+-- " + es_index_kg_api_tender_document + ": " + id)
	return True

        

##################################
# main
##################################

iteracion_search(IDTENDER_SEARCH)
iteracion_contracting_process (TOTAL_DATOS_CONTRACTING_PROCESS)
iteracion_tender (TOTAL_DATOS_TENDER)
iteracion_award (TOTAL_DATOS_AWARD)

f.write("\n")
f.write("Numero de elementos insertados: "+ str(len(list_of_id)) + "\n")
f.write("Numero de elementos omitidos por no tener informacion el kn-api: "+ str(len(list_of_id_void)) + "\n")
f.write("\n")

f.write(" + Fin del proceso de carga de datos" + "\n")

f.close()
