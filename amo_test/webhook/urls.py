from django.urls import path
from . import views

urlpatterns = [
    path('amo/', views.webhook_endpoint, name='webhook_endpoint'),

]
