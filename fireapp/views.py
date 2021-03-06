from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyrebase
from datetime import date
from pyfcm import FCMNotification
from django.db import connections
from Parent_api.models import ManagerParent
from django.db.models import Q

# Remember the code we copied from Firebase.
# This can be copied by clicking on the settings icon > project settings, then scroll down in your firebase dashboard

# config = {
#     "apiKey": "AIzaSyBVlQbdFekQRIEQcfNkXQYcuIabxTJr7YE",
#     "authDomain": "trackware-auth0.firebaseapp.com",
#     "databaseURL": "https://trackware-auth0.firebaseio.com",
#     "projectId": "trackware-auth0",
#     "storageBucket": "trackware-auth0.appspot.com",
#     "messagingSenderId": "404758940845",
#     "appId": "1:404758940845:web:19c2ebf3323760ff"
# }


config = {
    "apiKey": "AIzaSyBs2DgXkohpuWM0htNuAPHnk6_5yz5IOdo",
    "authDomain": "odoo-test1-6d92c.firebaseapp.com",
    "databaseURL": "https://odoo-test1-6d92c-default-rtdb.firebaseio.com",
    "projectId": "odoo-test1-6d92c",
    "storageBucket": "odoo-test1-6d92c.appspot.com",
    "messagingSenderId": "761759455686",
    "appId": "1:761759455686:web:9621a5608d0f564ab47ac7"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


@api_view(['GET'])
def Get_last_bus_location(request, bus_id, school_name):
    if request.method == 'GET':
        fullRound = school_name + "-round-" + str(bus_id)
        curr_date = date.today()
        #     # here we are doing firebase authentication
        # print("name sssssssssss11", request.build_absolute_uri())
        route = []

        # from firebase_admin.messaging import Message, Notification
        # from fcm_django.models import FCMDevice
        # message = Message(
        #     notification=Notification(2
        #         title="title",
        #         body="sentence",
        #     ),
        # )
        #
        # try:
        #     devices = FCMDevice.objects.all()
        #     devices.send_message(message)
        #
        # except Exception as e:
        #     print('Push notification failed.', e)

        # push_service = FCMNotification(api_key="AAAAsVxm2cY:APA91bGJ4jG6by56tl1z2HKmiTynaz6BXLmFaPwuk5NdytixIyxTS11iTPaXywVsQxnwmhSZRvUO5SsIioULD9qHCFK_6rVtnE5yQeIs7G3LzvDYUNd7jVEjJqvfnZbTspTE_xXWCSnO")
        # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
        # message_title = "Uber update"
        # message_body = "Hi Yousef, your customized news for today is ready"
        # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
        #                                            message_body=message_body)
        # #
        # print(result)

        try:
            for key, value in database.child('ghs-round-10').child('2022-02-22').get().val().items():
                route.append(value)
            lat = route[-1][0]
            long = route[-1][1]
            result = {
                "lat": float(lat) if lat else 0,
                "long": float(long) if long else 0
            }
        except:
            result = {
                "lat": 1,
                "long": 0
            }

        return Response(result)


@api_view(['POST'])
def Get_round_locations(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        round_id = request.data.get('round_id')
        fullRound = school_name + "-round-" + str(round_id)
        date = request.data.get('date')
        #     # here we are doing firebase authentication
        # print("name sssssssssss11", request.build_absolute_uri())
        route = []
        try:
            for key, value in database.child('ghs-round-10').child('2022-02-22').get().val().items():
                route.append(value)
            result = {
                "route": route
            }
        except:
            result = {
                "route": route
            }

        return Response(result)


@api_view(['POST'])
def send_school_message(request):
    # push_service = FCMNotification(
    #     api_key="AAAAwJiGQL0:APA91bH0yzNqpkRvB8hgnz64g-OKSjjGJADjtr8njfmY_EuucOAXFciONvfn9ooxqkkPHb3Mt9wZ2LLEEfQn4KFVkKfS8A_7sMQh9mjHUXsGLBseO31m_zOy9c39k3wwim8x0ojvw6ia")
    # title_ios = str("???????????? " + "???" + " ???/??? ?????????????????????!")
    # message_ios = str("???????????????~")
    # try:
    #     toke_ = [
    #         "ec575CPxhj8:APA91bEd64mo-Qw_a6mKYmEIgJ3ui4_qOv_6Cd96XRoHiDeR_IX_zbliwvdNDyNAbASmut9tuPPgY00MzUlVRP33x11I6YxfRY2T-Syli8U0FeJ1L2AuClaIa5PhbzR0uLvouDmOwfXQ"]
    #     result = push_service.notify_single_device(registration_id=toke_[0], message_title=title_ios,
    #                                                message_body=message_ios)
    #     # result = push_service.notify_multiple_devices(message_title=title_ios, message_body=message_ios, registration_ids=toke_, data_message={})
    # except Exception as e:
    #     print(e)
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        message_id = request.data.get('message_id')
        with connections[school_name].cursor() as cursor:
            cursor.execute(
                "select  message,title  from school_message where id = %s",
                [message_id])
            school_message = cursor.fetchall()
            cursor.execute(
                "select  student_student_id  from school_message_student_student where school_message_id = %s",
                [message_id])
            school_message_student_student = cursor.fetchall()
            r_id = []
            for id in school_message_student_student:
                r_id.append(id[0])
            cursor.execute(
                "select  mother_id,father_id,responsible_id_value from student_student WHERE id in %s ",
                [tuple(r_id)])
            columns = (x.name for x in cursor.description)
            student = cursor.fetchall()
            id = []
            for rec in student:
                if rec[0]:
                    id.append(rec[0])
                if rec[1]:
                    id.append(rec[1])
                if rec[2]:
                    id.append(rec[2])
            cursor.execute(
                "select  id from school_parent WHERE id in %s ",
                [tuple(id)])
            columns = (x.name for x in cursor.description)
            parent = cursor.fetchall()
            parent_id = []
            for rec in student:
                parent_id.append(rec[0])
            mobile_token = ManagerParent.objects.filter(Q(user_id=parent_id) and Q(db_name=school_name)).values_list(
                'mobile_token').order_by('-pk')[0]
            token = []
            for tok in mobile_token:
                token.append(tok)

            push_service = FCMNotification(
                api_key="AAAAsVxm2cY:APA91bGJ4jG6by56tl1z2HKmiTynaz6BXLmFaPwuk5NdytixIyxTS11iTPaXywVsQxnwmhSZRvUO5SsIioULD9qHCFK_6rVtnE5yQeIs7G3LzvDYUNd7jVEjJqvfnZbTspTE_xXWCSnO")
            registration_id = [
                "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"]
            message_title = school_message[0][1]
            message_body = school_message[0][0]
            result = push_service.notify_multiple_devices \
                (message_title=message_title, message_body=message_body, registration_ids=registration_id,
                 data_message={})
            #
            result1 = {
                "route": 'Ok'
            }

        return Response(result1)


@api_view(['POST'])
def send_confirmation_message_to_parent(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        student_name = request.data.get('student_name')
        parent_id = request.data.get('parent_id')
        mobile_token = ManagerParent.objects.filter(Q(user_id=parent_id) and Q(db_name=school_name)).values_list(
            'mobile_token').order_by('-pk')[0]
        for e in mobile_token:
            mobile_token = e[0]
        # print("mmmmmmmmmmmmmmm",len(mobile_token),mobile_token)
        push_service = FCMNotification(
            api_key="AAAAsVxm2cY:APA91bGJ4jG6by56tl1z2HKmiTynaz6BXLmFaPwuk5NdytixIyxTS11iTPaXywVsQxnwmhSZRvUO5SsIioULD9qHCFK_6rVtnE5yQeIs7G3LzvDYUNd7jVEjJqvfnZbTspTE_xXWCSnO")
        # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
        registration_id = mobile_token
        message_title = "Uber update"
        message_body = "please confirm that you have picked up" + student_name + "from the school"
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)
        #
        # print(result)
        result1 = {
            "route": 'Ok'
        }

        return Response(result1)


@api_view(['POST'])
def push_notification(request):
    if request.method == 'POST':
        action = request.data.get('action')
        avatar = request.data.get('avatar')
        endpoint_arn = request.data.get('endpoint_arn')
        message = request.data.get('message')
        platform = request.data.get('platform')
        round_id = request.data.get('round_id')
        school_id = request.data.get('school_id')
        title = request.data.get('title')
        user_id = request.data.get('user_id')
        user_ids = request.data.get('user_ids')
        mobile_token=[]
        for rec in user_ids:
            mobile_token1 = ManagerParent.objects.filter(Q(user_id=rec) and Q(db_name=school_id)).values_list(
                'mobile_token').order_by('-pk')[0]
            for e in mobile_token1:
                mobile_token.append(e[0])

        # for e in mobile_token:
        #     mobile_token = e[0]
        # print("mmmmmmmmmmmmmmm",len(mobile_token),mobile_token)
        push_service = FCMNotification(
            api_key="AAAAsVxm2cY:APA91bGJ4jG6by56tl1z2HKmiTynaz6BXLmFaPwuk5NdytixIyxTS11iTPaXywVsQxnwmhSZRvUO5SsIioULD9qHCFK_6rVtnE5yQeIs7G3LzvDYUNd7jVEjJqvfnZbTspTE_xXWCSnO")
        # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
        registration_id = mobile_token
        message_title = title
        message_body = message
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)
        result1 = {
            "route": 'Ok'
        }

        return Response(result1)
