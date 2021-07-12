from django.urls import path
from .views import monitoring, save_data_to_influxdb, monitoring_with_details, monitoring_with_ip_address

urlpatterns = [
    path('get-all', monitoring, name="monitoring"),
    path('get-all/<slug:ipaddress>', monitoring_with_ip_address, name="test_get_id"),
    path('get-all-detailed', monitoring_with_details, name="monitoring_with_details"),
    path('save-all', save_data_to_influxdb, name="save_data"),
]
