from django.urls import path
from . import views

# app_name='cost_analysis'

urlpatterns = [
    path('', views.fetch_default, name='fetch_default'),
    path('revenue/', views.revenue, name='revenue_ca'),
]
