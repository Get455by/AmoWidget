import requests
import json

data = {
    'name': 'IVAN',
    'email': 'masssssssss231ss22il@ivan.com',
    'phone': '1112233123211',

}

response = requests.get('http://127.0.0.1:8000/api/v1/send', params=data)
print(response.json())


# ?name=dgsd&phone=31432&email=sdfds
