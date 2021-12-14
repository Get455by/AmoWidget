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
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": self.code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.url + self.url_prefix, data=data)
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
        response = requests.post(self.url + self.url_prefix, data=data)
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

    def create_contact(self, name, phone, email):
        headers = super().get_headers()

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
            AmoMain().refresh_access_token()
            add_contact_responce = requests.post(self.url + self.url_prefix, json=add_data,
                                                 headers=super().get_headers())
        return add_contact_responce.json()["_embedded"]["contacts"][0]['id'], 'created'

    def get_contact_by_id(self, contact_id):
        headers = super().get_headers()
        contact_info = requests.get(self.url + self.url_prefix + '/' + str(contact_id), headers=headers)
        if contact_info.status_code != 200:
            AmoMain().refresh_access_token()
            contact_info = requests.get(self.url + self.url_prefix + '/' + str(contact_id),
                                        headers=super().get_headers())
        return contact_info.json()


class AmoLeads(AmoMain):
    url_prefix = '/api/v4/leads'

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

        add_new_lead = requests.post(self.url + self.url_prefix, json=add_lead_data, headers=headers)
        if add_new_lead.status_code != 200:
            AmoMain().refresh_access_token()
            add_new_lead = requests.post(self.url + self.url_prefix, json=add_lead_data, headers=super().get_headers())

    def get_leads_by_id(self, lead_id):
        headers = super().get_headers()
        lead_info = requests.get(self.url + self.url_prefix + '/' + str(lead_id) + '?with=_embedded,contacts',
                                 headers=headers)
        return lead_info.json()


class AmoTask(AmoMain):
    url_prefix = '/api/v4/tasks'

    def add_task(self, entity_id, entity_type, text, complete_till):
        headers = super().get_headers()
        add_data = {'add':
            {
                "task_type_id": 1,
                "text": text,
                "complete_till": complete_till,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "request_id": "example"
            }}
        task = requests.post(self.url + self.url_prefix, json=add_data, headers=headers)
        return task.json()


class AmoNote(AmoMain):

    def add_note(self, entity_type, entity_id, text_note):
        headers = super().get_headers()
        params = [{
            "entity_id": entity_id,
            "note_type": "common",
            "params": {
                "text": text_note
            }}]
        task = requests.post('https://usatest.amocrm.com/api/v4/' + entity_type + '/notes', json=params,
                             headers=headers)

        return task.json()