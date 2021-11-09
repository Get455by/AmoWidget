from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
import json
import requests


access_token = settings.ACCESS_TOKEN
headers = {
    'Authorization': 'Bearer ' + access_token
    }




#homepage view
def contact(request):
    return render(request, 'pages/index.html')

#send_contact to AmoCRM view
def send_contact(request):
    print ('ok')
    #get data
    name = request.GET.get('name')
    email = request.GET.get('email')
    phone = request.GET.get('phone')


    # data for add and edit Amo contacts
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
            print(i)
            params['query'] = i
            response = requests.get('https://managertetsingapi.amocrm.ru/api/v4/contacts',params=params, headers=headers )
            if response.status_code == 200:
                response = response.json()
                # find in response contact's id
                if i == email:
                    find_contact_id_by_email = response["_embedded"]["contacts"][0]['id']
                elif i == phone:
                    find_contact_id_by_phone = response["_embedded"]["contacts"][0]['id']

        print(find_contact_id_by_email,find_contact_id_by_phone)
    except:
        print('no find contacts')
    # IF no similar contact in Amo contact list >> add new contact to Amo
    # and create new lead
    if find_contact_id_by_email == 'none' and find_contact_id_by_phone == 'none':
        try:
            add_contact_responce = requests.post('https://managertetsingapi.amocrm.ru/api/v4/contacts',json=add_data, headers=headers )
            if add_contact_responce.status_code == 200:
                new_contact_id = add_contact_responce.json()["_embedded"]["contacts"][0]['id']
                print(new_contact_id)


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
                print(add_new_lead.json())
        except Exception as ex:
            print(ex)

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

        edit_contact_responce = requests.patch('https://managertetsingapi.amocrm.ru/api/v4/contacts',json=edit_data, headers=headers )
        print(edit_contact_responce.json())
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
        add_new_lead = requests.post('https://managertetsingapi.amocrm.ru/api/v4/leads/complex',json=add_lead_data_edit, headers=headers )

    return redirect('home')
