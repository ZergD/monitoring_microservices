from django.urls import path
from .views import monitoring, save_data_to_influxdb, monitoring_with_details

urlpatterns = [
    path('get-all', monitoring, name="monitoring"),
    path('get-all-detailed', monitoring_with_details, name="monitoring_with_details"),
    path('save-all', save_data_to_influxdb, name="save_data"),
]
