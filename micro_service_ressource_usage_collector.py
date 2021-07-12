"""
@Author: Marc Mozgawa
@Date 11/07/21

This file starts the cpu_memory_monitoring agent/microservice
"""

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from timeloop import Timeloop
from datetime import timedelta, datetime
import click
import psutil
import time
import requests
import socket
import os

REST_API_ADDRESS = "http://127.0.0.1:8000/ressources-usage/save-all"

tl = Timeloop()


# def test_with_influxdb():
#     """
#     This is a test function to remind myself Influxdb command lines.
#     :return:
#     """
#     # initialize the Client
#     token = "WaKfamDkoQH3xbcbJo221YouLyMyaWLfQwqObjXxtGVcednoNXqZ4HglpRS5JS_HueepINFfgBzCe1xzLcMT2A=="
#     org = "myorg"
#     bucket = "monitoring"
#     client = InfluxDBClient(url="http://localhost:8086", token=token)
#
#     # lets write data
#     write_api = client.write_api(write_options=SYNCHRONOUS)
#
#     data = "mem,host=host1 used_percent=23.43234543"
#     # write_api.write(bucket, org, data)
#
#     point = Point("mem") \
#         .tag("host", "host1") \
#         .field("used_percent", 23.43234543) \
#         .time(datetime.utcnow(), WritePrecision.NS)
#
#     write_api.write(bucket, org, point)
#
#     p2 = Point("cpu_usage_percent").tag("ip", "192.188.1.1").tag("process", "processname1").field("value", 25.3)
#     write_api.write(bucket, org, p2)
#
#     print("writing to InfluxDB...")
#
#     # every 10sec pull all data
#     # transform them into correct format
#     # send PUT request


@click.command()
@click.option("--debug", is_flag=True, help="Allows to see the full logs")
def run(debug):
    if debug:
        print("Debug is True")
    else:
        print("Debug is False")

    start_process()


@tl.job(interval=timedelta(seconds=10))
def start_monitoring_specific_processes():
    """
    Function gets started by tl.start()
    It is run as a thread every 10secs

    Every 10 seconds:
        - gets mem_usage and cpu_usage from all processes
        - Bundles all results into a payload
        - Send a PUT request to monitoring_REST_server
            -> the server then saves data to Influxdb

    The template for sending information will be as follows:
    [
        {
            "timestamp": Unixtimestamp.
            "value": 50 # en pourcentage
            "process_name": "process1"
            "type": "cpu" # ici ça sera soit cpu soit mem
        },
        {
            "timestamp": Unixtimestamp.
            "value": 10 # en pourcentage
            "process_name": "process1"
            "type": "mem" # ici ça sera soit cpu soit mem
        }
    ]
    """
    unix_timestamp = None
    cpu_value = None
    mem_value = None
    process_name = None
    # cpu or mem
    type_data = None

    payload = {
        "data": []
    }

    print("Starting... start_monitoring_specific_processes...")
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
        # sometimes a process comes and goes away. Needed to avoid errors
        except:
            continue

        # if p.name() == "chrome.exe":
        mem_value = p.memory_percent()
        cpu_value = p.cpu_percent()
        process_name = p.name()
        txt_to_display_mem = "Process: [{}] has a memory usage of: [{}]".format(p.name(), p.memory_percent())
        txt_to_display_cpu = "Process: [{}] has a cpu usage of: [{}]".format(p.name(), p.cpu_percent())
        print(txt_to_display_mem)
        print(txt_to_display_cpu)
        print("--------------------------------------------------------------------------")

        unix_timestamp = time.time()

        # construct the payload/JSON format, First you Dict then smooth transform into JSON
        payload_mem = {
            "timestamp": unix_timestamp,
            "value": mem_value,
            "process_name": process_name,
            "type_data": "mem"
        }

        payload_cpu = {
            "timestamp": unix_timestamp,
            "value": cpu_value,
            "process_name": process_name,
            "type_data": "cpu"
        }

        payload["data"].append(payload_mem)
        payload["data"].append(payload_cpu)
        try:
            ipaddress = socket.gethostbyname("www.google.com")
        except:
            ipaddress = "0.0.0.0"
        payload["ipaddress"] = str(ipaddress)

    response = requests.put(REST_API_ADDRESS, json=payload)
    print("Response: ", response)
    print(response.text)


def start_process():
    """
    Starts the periodic "start_monitoring_specific_processes" calls with tl.start()
    """
    # while This run. If False. Then stop looping.
    bool_agent_power_status = True

    # will automatically shut down the jobs gracefully when the program is killed with block=True
    # This start the functions using the decorator tl.job()
    tl.start()
    while bool_agent_power_status:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            tl.stop()
            break


if __name__ == '__main__':
    print("Monitoring started...")
    run()
