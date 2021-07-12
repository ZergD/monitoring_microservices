# Monitoring_microservices

A REST server with Django framework with multiple endpoints to save and get ressource usage data.

Developped with Python3.9 on Windows10. Tested only on Windows10. Should work on Linux though.

## Microservices

### Microservice n°1: the ressource_usage_collector

Placed at the root of the project. The file "micro_service_ressource_usage_collector.py" acts like a "daemon". Launch it
and it will:

* Periodically gather memory_usage and cpu_usage in percent, per processes.
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

## Get alarm

http://127.0.0.1:8000/query-alarm/

A GET request allows the client to know:
what color the alert is. Orange. Red.

## Docker

Docker information here

## Improvement / Optimization Ideas

While working on the project. Those are the ideas I put on the side because I had little time.

### Improvement Ideas:

* The microservices are started/stopped manually. We could start/stop then with some network calls.
* Create another microservice only dedicated for prediction ? Use Keras to build a predictive model and train it.
* If the microservices can't connect to the REST server => raises ConnectionError and stop working. -> nothing was done
  for it try to reconnect after a couple of time.

### Optimizations Ideas:

* I am currently saving Point after Point.
* We could regroup them in a batch:
    - Another way would be:
      on the server side, to put everything into a Datatrame, and we can write a whole dataframe to influx db ?
        - are the performance way better ? To be tested.
