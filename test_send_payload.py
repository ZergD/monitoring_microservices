import pprint

import requests
from influxdb_client import InfluxDBClient
from statistics import mean
import operator
import json


def test_get_ressources_usage():
    response = requests.get("http://127.0.0.1:8000/ressources-usage/get-all")
    print(response)
    print("------------------")

    json_response = response.json()
    pprint.pprint(json_response)


def test_get_ressources_usage_detailed():
    response = requests.get("http://127.0.0.1:8000/ressources-usage/get-all-detailed")
    print(response)
    print("------------------")

    json_response = response.json()
    pprint.pprint(json_response)


def test_get_data_from_influxdb_old():
    org = "myorg"
    bucket = "monitoring"
    token = "WaKfamDkoQH3xbcbJo221YouLyMyaWLfQwqObjXxtGVcednoNXqZ4HglpRS5JS_HueepINFfgBzCe1xzLcMT2A=="
    client = InfluxDBClient(url="http://localhost:8086", token=token)

    query = 'from (bucket: "monitoring")' \
            ' |> range(start: -3h, stop: now())' \
            ' |> filter(fn: (r) => r._measurement == "mem_usage_percent")' \
            ' |> group(columns: ["process"])'
    print(query)

    tables = client.query_api().query(query, org=org)
    # tables = client.query_api().query_data_frame(query, org=org)

    print(tables)
    print(type(tables))

    # print(tables.tail())

    # here is the part where we iterate over the result query and construct a clean dict with all results.
    results = []
    dict_results = {}
    for table in tables:
        for i, record in enumerate(table.records, 0):
            # if i > 10:
            #     break

            current_process = record.values.get("process")

            if current_process not in dict_results.keys():
                dict_results[current_process] = [record.get_value()]
            else:
                dict_results[current_process].append(record.get_value())

            print("current process: ", current_process)
            results.append((record.get_field(), record.get_value(), record.values.get("process")))

    # print(results)
    # pprint.pprint(results)
    # pprint.pprint(dict_results)

    # here is the part where we create a mean results for all processes
    dict_mean_results = {}
    for elem in dict_results.keys():
        if elem not in dict_mean_results.keys():
            dict_mean_results[elem] = mean(dict_results[elem])

    # final mean results
    print("Final mean results by processes")
    pprint.pprint(dict_mean_results)

    # here we sort the dictionnary by value in ascending order
    sorted_final_dict_results = sorted(dict_mean_results.items(), key=operator.itemgetter(1))
    print("Final SORTED mean results by processes")
    pprint.pprint(sorted_final_dict_results)

    print("========================== JSON ==========================")
    json_payload = json.dumps(sorted_final_dict_results)
    pprint.pprint(json_payload)


def test_get_data_from_influxdb(measurement_filter: str):
    """
    This function queries the DB.
    Gathers, computes the mean of all values, and sorts all results
    :param measurement_filter: has to be "mem_usage_percent" or "cpu_usage_percent" or it will fail
    :return: 
    """
    # check input arg
    if measurement_filter != "mem_usage_percent" and measurement_filter != "cpu_usage_percent":
        print("Problem with measurement filter, has to be mem_usage_percent or cpu_usage_percent")
        return {"Fail": "problem with measurement filter"}

    org = "myorg"
    bucket = "monitoring"
    token = "WaKfamDkoQH3xbcbJo221YouLyMyaWLfQwqObjXxtGVcednoNXqZ4HglpRS5JS_HueepINFfgBzCe1xzLcMT2A=="
    client = InfluxDBClient(url="http://localhost:8086", token=token)

    query = f'from (bucket: "monitoring")' \
            f' |> range(start: -3h, stop: now())' \
            f' |> filter(fn: (r) => r._measurement == "{measurement_filter}")' \
            f' |> group(columns: ["process"])'
    print(query)

    tables = client.query_api().query(query, org=org)
    # tables = client.query_api().query_data_frame(query, org=org)

    print(tables)
    print(type(tables))

    # print(tables.tail())

    # here is the part where we iterate over the result query and construct a clean dict with all results.
    results = []
    dict_results = {}
    for table in tables:
        for i, record in enumerate(table.records, 0):
            # if i > 10:
            #     break

            current_process = record.values.get("process")

            if current_process not in dict_results.keys():
                dict_results[current_process] = [record.get_value()]
            else:
                dict_results[current_process].append(record.get_value())

            print("current process: ", current_process)
            results.append((record.get_field(), record.get_value(), record.values.get("process")))

    # print(results)
    # pprint.pprint(results)
    # pprint.pprint(dict_results)

    # here is the part where we create a mean results for all processes
    dict_mean_results = {}
    for elem in dict_results.keys():
        if elem not in dict_mean_results.keys():
            dict_mean_results[elem] = mean(dict_results[elem])

    # final mean results
    print("Final mean results by processes")
    pprint.pprint(dict_mean_results)

    # here we sort the dictionnary by value in ascending order
    sorted_final_dict_results = sorted(dict_mean_results.items(), key=operator.itemgetter(1))
    print("Final SORTED mean results by processes")
    pprint.pprint(sorted_final_dict_results)

    print("========================== JSON ==========================")
    json_payload = json.dumps(sorted_final_dict_results)
    pprint.pprint(json_payload)


# test_get_ressources_usage()
# test_get_data_from_influxdb("mem_usage_percent")
# test_get_data_from_influxdb("cpu_usage_percent")

test_get_ressources_usage()
# test_get_ressources_usage_detailed()
