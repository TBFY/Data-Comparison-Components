import time
import os


f = open("/python/salida.log", "a")
f.write("Inicio del proceso de carga de datos" + "\n")
f.write("Variables de Entorno:" + "\n")
f.write("ID del Tender a consultar: " + os.environ.get('IDTENDER') + "\n")
f.write("LIMITE del numero de consultas a realizar: " + os.environ.get('LIMITE') + "\n")


# wait for yellow status
#for _ in range(1 if nowait else 100):
#    try:
#        client.cluster.health(wait_for_status='yellow')
#    except ConnectionError:
#        time.sleep(.1)
#else:
#    # timeout
#    raise SkipTest("Elasticsearch failed to start.")
		


f.write("Fin del proceso de carga de datos" + "\n")

f.close()