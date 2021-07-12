# Create your views here.
import os
import pprint
from datetime import datetime

import psutil
import pandas as pd
from django.shortcuts import HttpResponse
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from statistics import mean
from collections import defaultdict
import operator
import json

import psutil
from django.http import HttpResponse

TOKEN = "WaKfamDkoQH3xbcbJo221YouLyMyaWLfQwqObjXxtGVcednoNXqZ4HglpRS5JS_HueepINFfgBzCe1xzLcMT2A=="
ORG = "myorg"
BUCKET = "monitoring"
URL_DB = "http://localhost:8086"


@api_view(['GET'])
def monitoring_with_ip_address(request, ipaddress):
    ipaddress = str(ipaddress).replace("-", ".")
    # str_to_display = "Hello world from Django! id= " + ipaddress
    # print(str_to_display)
    # print("new ipaddress = ", ipaddress)
    # return Response(str_to_display, status=status.HTTP_200_OK)

    res = None
    if request.method == "GET":
        res_mem = get_data_from_influx_db("mem_usage_percent", ipaddress=ipaddress)
        res_cpu = get_data_from_influx_db("cpu_usage_percent", ipaddress=ipaddress)

        # here we merge both dictionnaries.
        res = defaultdict(list)
        for d in (res_mem, res_cpu):
            for key, value in d.items():
                res[key].append(value)

    return Response(json.dumps(res), status=status.HTTP_200_OK)


@api_view(['GET'])
def monitoring(request):
    res = None
    if request.method == "GET":
        res_mem = get_data_from_influx_db("mem_usage_percent", )
        res_cpu = get_data_from_influx_db("cpu_usage_percent")

        # here we merge both dictionnaries.
        res = defaultdict(list)
        for d in (res_mem, res_cpu):
            for key, value in d.items():
                res[key].append(value)

    return Response(json.dumps(res), status=status.HTTP_200_OK)


def get_data_from_influx_db(measurement_filter: str, detail_flag=False, ipaddress=None) -> json:
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

    range_start = "-3h"
    # org = "myorg"
    # bucket = "monitoring"
    # token = "WaKfamDkoQH3xbcbJo221YouLyMyaWLfQwqObjXxtGVcednoNXqZ4HglpRS5JS_HueepINFfgBzCe1xzLcMT2A=="
    client = InfluxDBClient(url=URL_DB, token=TOKEN)

    if ipaddress is None:
        query = f'from (bucket: "monitoring")' \
                f' |> range(start: {range_start}, stop: now())' \
                f' |> filter(fn: (r) => r._measurement == "{measurement_filter}")' \
                f' |> group(columns: ["process"])'
    else:
        query = f'from (bucket: "monitoring")' \
                f' |> range(start: {range_start}, stop: now())' \
                f' |> filter(fn: (r) => r._measurement == "{measurement_filter}")' \
                f' |> filter(fn: (r) => r.ip == "{ipaddress}")' \
                f' |> group(columns: ["process"])'
    print(query)

    tables = client.query_api().query(query, org=ORG)
    # tables = client.query_api().query_data_frame(query, org=org)

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

            # print("current process: ", current_process)
            results.append((record.get_field(), record.get_value(), record.values.get("process")))

    # print(results)
    # pprint.pprint(results)
    # pprint.pprint(dict_results)

    # here is the part where we create a mean results for all processes
    dict_mean_results = {}
    for elem in dict_results.keys():
        if elem not in dict_mean_results.keys():
            if detail_flag:
                dict_mean_results[elem] = dict_results[elem]
            else:
                dict_mean_results[elem] = mean(dict_results[elem])

    # final mean results
    # print("Final mean results by processes")
    # pprint.pprint(dict_mean_results)

    # here we sort the dictionnary by value in ascending order
    # sorted_final_dict_results = sorted(dict_mean_results.items(), key=operator.itemgetter(1))

    # print("Final SORTED mean results by processes")
    # pprint.pprint(sorted_final_dict_results)

    # print("========================== JSON ==========================")
    # json_payload = json.dumps(sorted_final_dict_results)
    # pprint.pprint(json_payload)
    # return json_payload

    # return sorted_final_dict_results

    return dict_mean_results


@api_view(['PUT'])
def save_data_to_influxdb(request):
    """
    Receives data from Micro service ressource usage collector
    and saves data to InfluxDB
    """
    data = JSONParser().parse(request)
    print("Data = ")
    pprint.pprint(data)

    try:
        prepare_and_send_data_to_influxdb(data)
    except:
        return Response({"Response": "NOk"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"Response": "Ok"}, status=status.HTTP_200_OK)


def prepare_and_send_data_to_influxdb(json_data: dict, debug=False):
    # initialize the Client
    point_name = None
    org = "myorg"
    bucket = "monitoring"
    client = InfluxDBClient(url=URL_DB, token=TOKEN)

    # lets write data
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for elem in json_data["data"]:
        timestamp = elem["timestamp"]
        value = elem["value"]
        process_name = elem["process_name"]
        type_data = elem["type_data"]

        if type_data == "cpu":
            point_name = "cpu_usage_percent"
        elif type_data == "mem":
            point_name = "mem_usage_percent"
        else:
            raise TypeError

        point = Point(point_name) \
            .tag("ip", json_data["ipaddress"]) \
            .tag("process", process_name) \
            .field("value", value) \
            .time(datetime.utcfromtimestamp(timestamp), WritePrecision.NS)

        write_api.write(BUCKET, ORG, point)
        if debug:
            print("Point written: [{}], [{}], [{}], [{}]".format(datetime.utcfromtimestamp(timestamp),
                                                                 process_name, type_data, value))

    print("writing to InfluxDB...")


@api_view(['GET'])
def monitoring_with_details(request):
    print("We are in monitoring_with_details")
    res = None
    res_mem = None
    if request.method == "GET":
        res_mem = get_data_from_influx_db("mem_usage_percent", detail_flag=True)
        print(res_mem)
        # res_cpu = get_data_from_influx_db("cpu_usage_percent", detail_flag=True)

        # here we merge both dictionnaries.
        # res = defaultdict(list)
        # for d in (res_mem, res_cpu):
        #     for key, value in d.items():
        #         res[key].append(value)

    return Response(res_mem, status=status.HTTP_200_OK)
