from django.urls import path

from . import views

urlpatterns = [
    path('', views.contact, name='home'),
    path('send/', views.send_contact, name='send_contact'),

]
