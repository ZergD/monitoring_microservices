from django.urls import path
from .views import monitoring, save_data_to_influxdb

urlpatterns = [
    path('get-all', monitoring, name="monitoring"),
    path('save-all', save_data_to_influxdb, name="save_data"),
]
