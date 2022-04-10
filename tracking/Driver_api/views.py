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
from itertools import chain

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


            cursor.execute("select id,name from transport_round WHERE driver_id = %s",[data_id_bus[0][0]])    
            columns2 = (x.name for x in cursor.description)        
            rounds_name = cursor.fetchall()


            # *------------------------------------------------------------------------------------------------*
            cursor.execute("select id,round_id,day_id from round_schedule WHERE round_id = %s",[rounds_name[0][0]])    
            columns3 = (x.name for x in cursor.description)        
            rounds_details = cursor.fetchall()

            
            cursor.execute("select count(student_id) from transport_participant WHERE round_schedule_id = %s",[rounds_name[0][0]])    
            columns4 = (x.name for x in cursor.description)        
            rounds_count_student = cursor.fetchall()
            

            day_list=[]
            for x,y,z in rounds_details:  
                cursor.execute("select  name  from school_day where id = %s",[z])    
                columns5 = (x.name for x in cursor.description)
                day_name = cursor.fetchall()
                day_list.append(list(day_name))
           

            result = {
                'driver_ID Bus_no' : str(data_id_bus)[1:-1],
                'driver_name' : str(driver_name)[1:-1],
                'list_days': str(day_list)[1:-1],
                'rounds_name':str(rounds_name)[1:-1]

            }        


            # *------------------------------------------------------------------------------------------------*
            # 1-List of active round
        
            cursor.execute("select  id,name  from transport_round WHERE is_active = %s",[True])
            columns = (x.name for x in cursor.description)
            active_round_list = cursor.fetchall()
            active_round_list=str(active_round_list)[1:-1]

            
            # 2-A student transferred to another round
            cursor.execute("select  student_id,source_round_id  from transport_participant WHERE source_round_id IS NOT %s",[None])
            columns = (x.name for x in cursor.description)
            student_transferred = cursor.fetchall()
            student_transferred_list = str(student_transferred)[1:-1]


            student_name_transferred = []
            for x,y in student_transferred:
                cursor.execute("select id,display_name_search from student_student WHERE id = %s",[x])
                columns = (x.name for x in cursor.description)
                student_transferred = cursor.fetchall()
                student_name_transferred.append(list(student_transferred))
            
            student_name_transferred_list = str(student_name_transferred)[1:-1]

        return Response(student_transferred_list)

# cursor.execute("select id,name from transport_round WHERE id = %s",[y])