from django.urls import path
from . import views

urlpatterns = [
    path('amo_lead_status_changed/', views.webhook_endpoint, name='webhook_endpoint'),

]
