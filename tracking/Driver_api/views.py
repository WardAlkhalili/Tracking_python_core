from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.db import connections
from django.http.response import Http404,JsonResponse
from django.http import HttpResponse
from django.core.serializers import serialize
from collections import ChainMap
from rest_framework import status
# Create your views here.


@api_view(['GET'])
def driver_login(request,pincode):

    if request.method == 'GET':
        
        school_name = Manager.pincode(pincode)
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  driver_id,bus_no  from fleet_vehicle WHERE bus_pin = %s",[pincode])
            columns = (x.name for x in cursor.description)
            data_id_bus = cursor.fetchall()

            cursor.execute("select name from res_partner WHERE id = %s",[data_id_bus[0][0]])    
            columns1 = (x.name for x in cursor.description)        
            driver_name = cursor.fetchall()


            cursor.execute("select name from transport_round WHERE driver_id = %s",[data_id_bus[0][0]])    
            columns2 = (x.name for x in cursor.description)        
            rounds_name = cursor.fetchall()


            
        return Response(rounds_name)


