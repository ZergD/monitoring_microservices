# Monitoring_microservices

A REST server with Django framework with multiple endpoints to save and get ressource usage data.

Developped with Python3.9 on Windows10. Tested only on Windows10. Should work on Linux though.

## Getting Started

This section is for quickly setting everything up and make it run.

## Microservices

### Microservice n°1: the ressource_usage_collector

Placed at the root of the project. The file "micro_service_ressource_usage_collector.py" acts like a "daemon". Launch it
and it will:

* Periodically (default=10sec) gather memory_usage and cpu_usage in percent, per processes.
* Send a PUT request with all gathered data to the monitoring_REST_server and the server saves the data in Influxdb.

### Microservice n°2: the ressource_usage_alarm

Placed at the root of the project. The file "micro_service_ressource_usage_collector.py" acts like a "daemon". Launch it
and it will:

* Periodically query the DB to get the latest usage information. If a cpu_usage_value or a mem_usage_value is superior
  than the threshold 80% then display the name of the process with the RED Alert tag.
* Based on the data gathered from the DB, compute the prediction and if a cpu_usage_value or a mem_usage_value is
  superior than the threshold 80% then display the name of the process with the AMBER Alert tag.

## Get ressources usage:

http://127.0.0.1:8000/ressources-usage/get-all

A GET request allows the client the get:
memory usage and cpu usage per processes for the last 5minutes. By default the result value are averages. The query
asked for the last 5min, we gather all results and compute a mean value of the past 5min.

The final payload looks like this:
{'process_name1': [memory_usage, cpu_usage], ...
'process_name1': [memory_usage, cpu_usage]} Below is an example of a python dictionnary view before getting transformed
into a json.

{'AdAppMgrSvc.exe': [0.1384696485453048, 0.0],
'AdAppMgrUpdater.exe': [0.07419333856813531, 0.0], ...
'wsl.exe': [0.03692514596289905, 0.0],
'wslhost.exe': [0.031640821544883124, 0.0]}

To get a **detailed usage value**, ie, with history values, without the mean computes there is another endpoint:
http://127.0.0.1:8000/ressources-usage/get-all-detailed

At the current moment it returns the list of all the measurements for a given process, for the mem_usage ressource.
I stopped this feature here because it doesnt make much sense to have all those measurements. The get-all with 
the mean compute is good.

An exemple of the output is:
{'AdAppMgrSvc.exe': [0.12842683941476413, 0.12847469737616335, 0.1279961177621713, 0.13799843169460493,
0.13799843169460493, 0.13799843169460493, ... , 0.1386445141734942, 0.1386445141734942, 0.1386445141734942]}

## Get alarm

http://127.0.0.1:8000/ressources-usage/query-alarm/

A GET request allows the client to know:
what color the alert is. Orange. Red.

## Docker

Docker information here

To launch the influx db
docker run -p 8086:8086 -v influxdb:/var/lib/influxdb2 influxdb


## Library Used
* BDD=> influxDB
Python client: library: influxdb-client

* To create Python Daemon => https://pypi.org/project/python-daemon/

* Pour faire les parametres -debug: https://github.com/pallets/click

* Pour le logging: https://docs.python.org/3/library/logging.html

* Pour avoir Cpu/Mem Usage: psutil

Idees pour Executer des taches periodiques:
* Celery beat => too heavy framework
* Using time.sleep => too simple ? not robust enough ?
* Using threading.Timer
* Using threading.Event
https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679
* ==> timeloop lib for periodic tasks.


## Improvement / Optimization Ideas

While working on the project. Those are the ideas I put on the side because I had little time.

### Improvement Ideas:

* The InfluxDB allows to clean DATA if the DATA history is > 2 days. Didnt have time to configure it.
* At the current moment, I compute the mean manually. The Flux language allows to easily query the InfluxDB, and it 
  allows to use "mean" fonction. But didnt have time to make it work. Hence why i did it manually at the moment.
* The microservices are started/stopped manually. We could start/stop then with some network calls.
* Create another microservice only dedicated for prediction ? Use Keras to build a predictive model and train it.
* If the microservices can't connect to the REST server => raises ConnectionError and stop working. -> nothing was done
  for it try to reconnect after a couple of time.
* Use SetupTools to package and create automatically a Docker image for the project ?

### Optimizations Ideas:

* I am currently saving Point after Point.
* We could regroup them in a batch:
    - Another way would be:
      on the server side, to put everything into a Datatrame, and we can write a whole dataframe to influx db ?
        - are the performance way better ? To be tested.
