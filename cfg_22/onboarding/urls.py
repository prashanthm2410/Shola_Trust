# onboarding/urls.py
from django.urls import path
from . import views
from cost_analysis import views as views_
urlpatterns = [
    path('', views.index, name='index'),  # Ensure this matches your view
    path('identify/', views.identify, name='identify'),
    path('/cost_analysis', views_.fetch_default, name='fetch_default'),
    path('save_data', views.save_data, name='save_data'),
    path('revenue/', views.revenue, name='revenue'),
]
