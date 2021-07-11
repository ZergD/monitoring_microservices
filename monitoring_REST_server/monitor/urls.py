from django.urls import path
from .views import monitoring

urlpatterns = [
    path('', monitoring, name="monitoring"),
]
