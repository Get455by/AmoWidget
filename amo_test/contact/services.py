import requests
import json

from django.conf import settings
from django.core.files.storage import default_storage


class AmoMain:

    url_prefix = '/oauth2/access_token'
    url = settings.URL
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    redirect_uri = settings.REDIREKT_URI
    code = settings.CODE


    # save a/r token to .json file
    def save_access_token(self, token):

        try:
            if token['token_type'] == "Bearer":
                with default_storage.open('access_token.json', 'w') as tok:
                    tok.write(str(token))
                print('New r/a tokens were generated and saved')
            else:
                print(f'Error: {token}')
        except:
            print(f'Error: {token}')

    # get a/r token from json file to future use
    def get_token_from_file(self):
        with default_storage.open('access_token.json', 'r') as tok:
            for line in tok:
                pass
            token = eval(line)
        print('r/a tokens were loaded from file')
        token = eval(line)
        return token

    # first one-time generate access token
    def get_access_token(self):
        data  = {
          "client_id": self.client_id,
          "client_secret": self.client_secret,
          "grant_type": "authorization_code",
          "code": self.code,
          "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.url + self.url_prefix, data=data )
        token = response.json()
        AmoMain().save_access_token(token)

    # refresh a/r tokens if there were expired
    def refresh_access_token(self):
        token = AmoMain().get_token_from_file()
        refresh_token = token['refresh_token']
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": self.redirect_uri
        }
        response = requests.post(self.url + self.url_prefix, data=data )
        token = response.json()
        print('r/a tokens were refreshed')
        AmoMain().save_access_token(token)

    # get headers for requests to Amo API

    def get_headers(self):
        token = AmoMain().get_token_from_file()
        access_token = token['access_token']
        headers = {'Authorization': 'Bearer ' + access_token}
        return headers


class AmoContact(AmoMain):

    url_prefix = '/api/v4/contacts'

    def find_similar_contacts(self, name, phone, email):
        headers = super().get_headers()
        params_list = [phone, email]
        for i in params_list:
            print(f'START')
            response = requests.get( self.url + self.url_prefix + '?query='+i, headers=headers)
            print(f'Response of checking contact {response}')
            if response.status_code == 200:
                print('[+] response.status_code == 200')
                response = response.json()
                # find in response contact's id
                find_contact_id_param = response["_embedded"]["contacts"][0]['id']
                print('ok')
                AmoContact().update_contact(find_contact_id_param, name, phone, email)
                return find_contact_id_param

        return False

    # Updating contact if similar was found

    def update_contact(self, find_contact_id_param, name, phone, email):
        headers = super().get_headers()
        add_data =[{
                "id": find_contact_id_param,
                "name": name,
                "custom_fields_values": [
                    {
                        'field_id':103141,
                        "values": [
                            {
                                "value": phone,
                                "enum_code": "WORK"
                            }
                            ],

                    },
                    {
                        'field_id':103143,
                        "values": [
                            {
                                "value": email,
                                "enum_code": "WORK"
                            }
                            ]
                    }
                ],
        }]

        update_contact_responce = requests.patch(self.url + self.url_prefix, json=add_data, headers=headers)
        if update_contact_responce.status_code != 200:
            super().refresh_access_token()
            update_contact_responce = requests.patch(self.url + self.url_prefix, json=add_data,
                                                     headers=super().get_headers())
        return update_contact_responce.json()

    def create_contact(self, name, phone, email):
        headers = super().get_headers()
        print('go to check similar contact')
        similar_contact = AmoContact().find_similar_contacts(name, phone, email)
        if similar_contact != False:
            print(f'Similar contact was found: {similar_contact}. It was updated')
            return similar_contact, 'updated'
        print(f'Similar contact was not found. Start adding new contact')
        add_data = {
            'add':
            {
                "name": name,
                "custom_fields_values": [
                    {
                        'field_id': 103141,
                        "values": [
                            {
                                "value": phone,
                                "enum_code": "WORK"
                            }
                            ],

                    },
                    {
                        'field_id': 103143,
                        "values": [
                            {
                                "value": email,
                                "enum_code": "WORK"
                            }
                            ]
                    }
                ],
            }
        }
        add_contact_responce = requests.post(self.url + self.url_prefix, json=add_data, headers=headers)
        if add_contact_responce.status_code != 200:
            super().refresh_access_token()
            add_contact_responce = requests.post(self.url + self.url_prefix, json=add_data, headers=super().get_headers())
        return add_contact_responce.json()["_embedded"]["contacts"][0]['id'], 'created'

class AmoLeads(AmoMain):

    def create_lead(self, contact_id):
        print(contact_id)
        headers = super().get_headers()
        add_lead_data = [{
                    "name": "Lead from my test",
                    "_embedded": {
                        "contacts": [
                            {
                                "id": contact_id
                            }
                        ]
                    }
        }]

        add_new_lead = requests.post('https://usatest.amocrm.com/api/v4/leads', json=add_lead_data, headers=headers)
