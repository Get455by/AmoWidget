from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_contact, name='send_contact'),
    path('lead/', views.add_lead, name='add_lead')
]
