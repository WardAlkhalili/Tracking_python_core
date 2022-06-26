from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyrebase
from datetime import date
from pyfcm import FCMNotification
from django.db import connections
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
        print("name sssssssssss11", request.build_absolute_uri())
        route=[]


        # from firebase_admin.messaging import Message, Notification
        # from fcm_django.models import FCMDevice
        # message = Message(
        #     notification=Notification(
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
            long =  route[-1][1]
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
        print("name sssssssssss11", request.build_absolute_uri())
        route=[]
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
    # title_ios = str("구독중인 " + "헿" + " 이/가 변경되었습니다!")
    # message_ios = str("민섭이혀엉~")
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
            push_service = FCMNotification(
                api_key="AAAAsVxm2cY:APA91bGJ4jG6by56tl1z2HKmiTynaz6BXLmFaPwuk5NdytixIyxTS11iTPaXywVsQxnwmhSZRvUO5SsIioULD9qHCFK_6rVtnE5yQeIs7G3LzvDYUNd7jVEjJqvfnZbTspTE_xXWCSnO")
            registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
            message_title = school_message[0][1]
            message_body = school_message[0][0]
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                       message_body=message_body)
            #
            print(result)
            result1 = {
                "route": 'Ok'
            }

        return Response(result1)

@api_view(['POST'])
def send_confirmation_message_to_parent(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        student_name = request.data.get('student_name')
        parent_id=request.data.get('parent_id')
        push_service = FCMNotification(
            api_key="AAAAsVxm2cY:APA91bGJ4jG6by56tl1z2HKmiTynaz6BXLmFaPwuk5NdytixIyxTS11iTPaXywVsQxnwmhSZRvUO5SsIioULD9qHCFK_6rVtnE5yQeIs7G3LzvDYUNd7jVEjJqvfnZbTspTE_xXWCSnO")
        registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
        message_title = "Uber update"
        message_body = "Hi Yousef, your customized news for today is ready"
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)
        #
        print(result)
        result1 = {
            "route": 'Ok'
        }

        return Response(result1)
