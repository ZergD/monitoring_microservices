# monitoring_microservices

A REST server with Django framework creates an endpoint at the adress:

## Get ressources usage:
http://127.0.0.1:8000/ressources-usage/

A GET request allows the client the get:
memory usage and cpu usage per processes for the last 5minutes


## Get alarm
http://127.0.0.1:8000/query-alarm/

A GET request allows the client to know:
what color the alert is. Orange. Red.
