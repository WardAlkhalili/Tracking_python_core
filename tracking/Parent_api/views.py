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
import datetime
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
            y = json.dumps(notifications)
            settings = "{\"notifications\":"+y+"}"
            cursor.execute(
                "UPDATE public.school_parent SET settings=%s WHERE id=%s;",
                [settings, 1])
            result = {
                'status': 'ok', }
            return Response(result)
    elif  request.method == 'GET':
        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  settings from school_parent WHERE id = %s", [2])
            columns = (x.name for x in cursor.description)
            data_id_bus = cursor.fetchall()
            if data_id_bus[0][0]:
                data=json.loads(data_id_bus[0][0])
                return Response(data)
            result = {'status':'Empty'}
            return Response(result)


@api_view(['POST', 'GET'])
def student_served(request):
    if request.method == 'POST':
        round_id = request.data.get('round_id')
        student_id = request.data.get('student_id')
        datetime_c = datetime.datetime.now()
        school_name = Manager.pincode('iks')
        with connections[school_name].cursor() as cursor:
            cursor.execute("select  activity_type from student_history WHERE round_id = %s AND student_id = %s AND datetime = %s ", [round_id,student_id,datetime_c])
            columns = (x.name for x in cursor.description)
            student_served = cursor.fetchall()
            if student_served:
                if student_served[0][0]=="out-school" or student_served[0][0]=="out":
                    result = {'result': True}
                    return Response(result)
            result = {'result': False}
            return Response(result)
    elif request.method == 'GET':
            # import hashlib
            #
            # plaintext = 9872058209
            # from hashlib import pbkdf2_hmac
            # dk = pbkdf2_hmac('sha512', b'password', b'bad salt' * 2, plaintext)
            #
            # dk.hex()
            # # instantiate sha3_256 object
            # # d = hashlib.sha3_256(plaintext)
            #
            # # generate binary bash of "hello" string
            # # hash = d.digest()
            # print(dk.hex())

            # # generate human readably hash of "hello" string
            # hash = d.hexdigest()
            # print(hash)
            result = {'status': 'error'}
            return Response(result)