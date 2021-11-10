from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
import json
import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


access_token = settings.ACCESS_TOKEN
headers = {
    'Authorization': 'Bearer ' + access_token
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def send_contact(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        email = request.GET.get('email')
        phone = request.GET.get('phone')
    else:
        return Response({'status':'fail', 'description':'only GET request is supported'})

    if not name or not email or not phone:
        return Response({'status':'fail', 'description':'Required argument is missing'})
    # data for add Amo contacts
    add_data = [
        {
            "name": name,
            "custom_fields_values": [
                {
                    'field_id':412703,
                    "values": [
                        {
                            "value": phone,
                            "enum_code": "WORK"
                        }
                        ],

                },
                {
                    'field_id':412705,
                    "values": [
                        {
                            "value": email,
                            "enum_code": "WORK"
                        }
                        ]
                }
            ],
        }
    ]


    # find contact by email or phone in Amo contactList
    find_contact_id_by_email = 'none'
    find_contact_id_by_phone = 'none'
    try:
        params = {}
        params_list = [phone,email]
        for i in params_list:
            params['query'] = i
            response = requests.get('https://managertetsingapi.amocrm.ru/api/v4/contacts',params=params, headers=headers )
            if response.status_code == 200:
                response = response.json()
                # find in response contact's id
                if i == email:
                    find_contact_id_by_email = response["_embedded"]["contacts"][0]['id']
                elif i == phone:
                    find_contact_id_by_phone = response["_embedded"]["contacts"][0]['id']
    except Exception as ex:
        return Response({'Status':'Fail', 'Description':'Something went wrong', 'Exeption':ex})

    # IF no similar contact in Amo contact list >> add new contact to Amo
    # and create new lead
    if find_contact_id_by_email == 'none' and find_contact_id_by_phone == 'none':

        try:
            add_contact_responce = requests.post('https://managertetsingapi.amocrm.ru/api/v4/contacts',json=add_data, headers=headers )

            if add_contact_responce.status_code == 200:
                new_contact_id = add_contact_responce.json()["_embedded"]["contacts"][0]['id']

                add_lead_data_new = [
                    {
                        "name": "Lead from my test",
                        "created_by": 0,
                        "_embedded": {
                            "contacts": [
                                {
                                    "id": new_contact_id
                                }
                            ]
                        }
                    },
                ]
                add_new_lead = requests.post('https://managertetsingapi.amocrm.ru/api/v4/leads/complex',json=add_lead_data_new, headers=headers )
                return Response({'Status':'Ok', 'Description':'A new contact has been added', 'Lead':'New lead added'})
        except Exception as ex:
            return Response({'Status':'Fail', 'Description':'Something went wrong', 'Exeption':ex})

    # IF find similar contact in Amo contact list >> edit current contact in Amo
    # and create new lead
    elif find_contact_id_by_email != 'none' or find_contact_id_by_phone != 'none':

        if find_contact_id_by_email != 'none':
            find_contact_id = find_contact_id_by_email
        elif find_contact_id_by_phone != 'none':
            find_contact_id = find_contact_id_by_phone

        edit_data = [
            {
                "id": find_contact_id,
                "name": name,
                "custom_fields_values": [
                    {
                        'field_id':412703,
                        "values": [
                            {
                                "value": phone,
                                "enum_code": "WORK"
                            }
                            ],

                    },
                    {
                        'field_id':412705,
                        "values": [
                            {
                                "value": email,
                                "enum_code": "WORK"
                            }
                            ]
                    }
                ],
            }
        ]
        # edit current contact
        try:
            edit_contact_responce = requests.patch('https://managertetsingapi.amocrm.ru/api/v4/contacts',json=edit_data, headers=headers )
        except Exception as ex:
            return Response({'Status':'Fail', 'Description':'Something Went Wrong', 'Exeption':ex})
        add_lead_data_edit = [
            {
                "name": "Lead from my test",
                "created_by": 0,
                "_embedded": {
                    "contacts": [
                        {
                            "id": find_contact_id
                        }
                    ]
                }
            },
        ]
        # add new lead
        try:
            add_new_lead = requests.post('https://managertetsingapi.amocrm.ru/api/v4/leads/complex',json=add_lead_data_edit, headers=headers )
            return Response({'Status':'Ok', 'Description':'The contact has been changed', 'Lead':'New lead added'})
        except Exception as ex:
            return Response({'Status':'Fail', 'Description':'Something went wrong', 'Exeption':ex})
    return Response({'Status':'Something went wrong'})
