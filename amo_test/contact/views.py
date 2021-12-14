from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

import json
import requests

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .services import *


@api_view(['GET'])
@permission_classes([AllowAny])
def get_hook(request):
    hooks = AmoWebhook().get_all_webhooks()
    return Response({'Status': 'gooddeal', 'Description': hooks})

@api_view(['GET'])
@permission_classes([AllowAny])
def add_lead(request):
    AmoLeads().create_lead(264999)
    return Response({'Status': 'gooddeal', 'Description': 'Something went wrong'})



@api_view(['GET'])
@permission_classes([AllowAny])
def send_contact(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        email = request.GET.get('email')
        phone = request.GET.get('phone')
        print('[+] Get success request')
    else:
        return Response({'status':'fail', 'description':'only GET request is supported'})

    if not name or not email or not phone:
        return Response({'status':'fail', 'description':'Required argument is missing!'})

    # Go to add contact func. Func will check for similar contact in
    # AmoCRM lists by phone and email, before adding. If similar
    # contact will be found - the old contact will be updated with income data
    try:
        id_contact, status = AmoContact().create_contact(name, phone, email)
        AmoLeads().create_lead(id_contact)
        if status == 'updated':
            return Response({'Status': 'Ok', 'Description': 'The contact has been changed', 'Lead': 'New lead added'})
        elif status == 'created':
            return Response({'Status': 'Ok', 'Description': 'A new contact has been added', 'Lead': 'New lead added'})

        return Response({'Status':'Ok', 'Description':'A new contact has been added', 'Lead':'New lead added'})
    except Exception as ex:
        return Response({'Status':'Fail', 'Description':'Something went wrong', 'Exeption':ex})


