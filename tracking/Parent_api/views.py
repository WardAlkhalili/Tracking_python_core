from django.shortcuts import render

# Create your views here.
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.db import connections
from django.http.response import Http404, JsonResponse
from django.http import HttpResponse
from django.core.serializers import serialize
from collections import ChainMap
from rest_framework import status
from itertools import chain
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json

# from ..Driver_api.models import *


@api_view(['POST', 'GET'])
def feed_back(request):
    if request.method == 'POST':
        student_id = request.data.get('student_id')
        feed_back = request.data.get('feed_back')
        impression = request.data.get('impression')
        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute(
                "INSERT INTO feed_back(model_id, model_type, feed_back, impression, student_id)VALUES (%s, %s,%s,%s,%s);",
                [25, 'App\Model\Parents', feed_back, 3, student_id])
            # cursor.execute("INSERT INTO feed_back(feed_back, impression, student_id)VALUES (%s, %s, %s);", [feed_back,impression,student_id])
            # columns = (x.name for x in cursor.description)
            # data_id_bus = cursor.fetchall()
            result = {
                'status': 'ok', }
            return Response(result)


@api_view(['POST', 'GET'])
def settings(request):
    if request.method == 'POST':
        notifications = request.data.get('notifications')

        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            settings = {
                'notifications':notifications
            }
            cursor.execute(
                "UPDATE public.school_parent SET settings=%s WHERE id=%s;",
                [str(settings), 1])
            result = {
                'status': 'ok', }
            return Response(result)
    elif  request.method == 'GET':
        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:

            cursor.execute("select  settings from school_parent WHERE id = %s", [1])
            columns = (x.name for x in cursor.description)
            data_id_bus = cursor.fetchall()

            print("ssssssssssssssssssssssss",data_id_bus[0][0])
            print(type(data_id_bus))
            # data=json.loads(data_id_bus[0][0])
            # print(data)
            result = {data_id_bus[0][0]}
        return Response(result)

