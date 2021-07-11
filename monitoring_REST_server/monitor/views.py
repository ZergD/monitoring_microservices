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

import psutil
from django.http import HttpResponse


@api_view(['GET', 'POST', 'PUT'])
def monitoring(request):
    res = "Hello"

    return Response({"Response": "Ok"}, status=status.HTTP_200_OK)
