import json
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

from contact.services import *

# Getting the current date and time
dt = datetime.now()

# getting the timestamp
ts = datetime.timestamp(dt)


@csrf_exempt
@require_POST
def webhook_endpoint(request):
    # request_data
    a = request.POST

    new_lead_status = int(list(dict(a).values())[2][0])
    entity_id = int(list(dict(a).values())[0][0])
    entity_type = 'leads'
    task_text = 'Test task for lead owner'
    complete_till = int(ts) + 86400

    # add task to lead and lead owner
    task = AmoTask().add_task(entity_id, entity_type, task_text, complete_till)

    # check if new_lead_status == meeting status
    # send email to leads contact
    if new_lead_status == 44714827:
        lead_info = AmoLeads().get_leads_by_id(entity_id)

        contact_id = lead_info['_embedded']['contacts'][0]['id']

        contact_info = AmoContact().get_contact_by_id(contact_id)

        contact_email = contact_info['custom_fields_values'][1]['values'][0]['value']

        send_mail('Meeting is scheduled ',
                  'The meeting will take place on 01.01.2022 at 6 am at your home. \nThe meeting will last 12 hours and we will discuss cleaning your apartment. \nThank you for choosing our company',
                  'amoadmin@noreply.com',
                  [contact_email],
                  fail_silently=False, )

        text = 'The meeting is scheduled'
        # add notes to contact card
        added_note = AmoNote().add_note('contacts', contact_id, text)

        return Response({'status': 'OK', 'description': 'Good'})
    else:
        return Response({'status': 'fail', 'description': 'Required argument is missing!'})


@api_view(['GET'])
@permission_classes([AllowAny])
def twilio_income(request):
    a = request.GET
    requests.get(
        "https://api.telegram.org/bot2082528189:AAGOISKjp_u9Q3Xm3ehGCHn-AXHNoUMjHgo/sendMessage?chat_id=-1001595963709&text=" + str(
            a))
    return Response({'status': 'OK', 'description': 'Good'})