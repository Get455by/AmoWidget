from django.urls import path
from . import views

urlpatterns = [
    path('amo_lead_status_changed/', views.webhook_endpoint, name='webhook_endpoint'),
    path('twilio_income/', views.twilio_income, name='twilio_income')

]
