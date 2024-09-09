from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyrebase
from datetime import date
from pyfcm import FCMNotification
from django.db import connections
from Parent_api.models import ManagerParent
from Driver_api.models import Manager
import firebase_admin
import requests
from firebase_admin import credentials
from google.oauth2 import service_account
import google.auth.transport.requests

from django.db.models import Q
from datetime import datetime
import calendar
import json
from threading import Timer
import re
from fireapp.models import ManagerTracker

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
# config = {
#     "apiKey": "AIzaSyCYVFzNlEcAP7mBstY59zB9CIEsa5W2bgc",
#     "authDomain": "field-service-management-da2ca.firebaseio.com",
#     "databaseURL": "https://field-service-management-da2ca.firebaseio.com",
#     "projectId": "field-service-management-da2ca",
#     "storageBucket": "field-service-management-da2ca.appspot.com",
#     "messagingSenderId": "132137361303",
#     "appId": "1:132137361303:android:ee543bda9568756c"
# }
config = {
    "apiKey": "AIzaSyAioXmXtdm0-5c5TruEgczV1B5uT43iZZA",
    "authDomain": "trackware-sms.firebaseapp.com",
    "databaseURL": "https://trackware-sms-default-rtdb.firebaseio.com",
    "projectId": "trackware-sms",
    "storageBucket": "trackware-sms.appspot.com",
    "messagingSenderId": "889780824569",
    "appId": "1:889780824569:android:9df33727f007d8ffa47528"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
cred = credentials.Certificate("/home/ec2-user/trackware-sms-82ee7532ea90.json")
# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred)
# default_app = firebase_admin.initialize_app()
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']


def _get_access_token():
    """Retrieve a valid access token that can be used to authorize requests.

    :return: Access token.
    """
    credentials = service_account.Credentials.from_service_account_file(
        '/home/ec2-user/trackware-sms-82ee7532ea90.json', scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


@api_view(['GET'])
def Get_last_bus_location(request, bus_id, school_name):
    if request.method == 'GET':
        fullRound = school_name + "-stg-round-" + str(bus_id)
        # print(fullRound)
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
        # print(database.child(fullRound).get().val().items())
        try:

            d = datetime.utcnow()
            unixtime = calendar.timegm(d.utctimetuple())

            now = datetime.today()
            # print(database.child(fullRound).child('2022-08-14').child('1660461821').get().val())
            location = database.child(fullRound).child(str(now.date())).get().val()

            # for key, value in database.child(fullRound).child('2022-08-14').child('1660461821').get().val():
            #     route.append(value)
            lat = list(location.items())[-1][1][0]
            long = list(location.items())[-1][1][1]

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


def send_message(token, body, title, data):
    print(token)
    headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }
    url = "https://fcm.googleapis.com/v1/projects/trackware-sms/messages:send"
    payload = json.dumps({
        "message": {
            "token": token,
            "notification": {
                "body": body,
                "title": title
            },
            "android": {
                "notification": {
                    "sound": "new_beeb"
                }
            },
            "apns": {
                "payload": {
                    "aps": {
                        "alert": {
                            "title": title,
                            "body": body
                        },
                        "sound": "new_beeb.mp3"
                    }
                }
            },
            # "data": data
        }
    })
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message. Status code: {r.status_code}")
        print(r.text)
    # print(r)


@api_view(['POST'])
def Get_round_locations(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        round_id = request.data.get('round_id')
        start_unix_time = request.data.get('start_unix_time')
        fullRound = school_name + "-stg-round-" + str(round_id)
        date = request.data.get('date').split('-')
        # print()
        currentDate = datetime.strptime(date[0] + "/" + date[1] + "/" + date[2], '%d/%m/%Y').date()

        route = []
        try:

            for key, value in database.child(fullRound).child(str(currentDate)).get().val().items():
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
        r = Timer(3.0, twoArgs, (message_id, school_name))
        r.start()
        result1 = {
            "route": 'Ok'

        }

    return Response(result1)


def twoArgs(message_id, school_name):
    result1 = {
        "route": 'Ok'

    }

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
        r_id = list(dict.fromkeys(r_id))

        if r_id:
            for std in r_id:
                cursor.execute(
                    "select  mother_id,father_id,responsible_id_value,display_name_search from student_student WHERE id = %s ",
                    [std])
                student = cursor.fetchall()
                student_name = ''
                id = []
                for rec in student:
                    student_name = rec[3]
                    if rec[0]:
                        id.append(rec[0])
                    if rec[1]:
                        id.append(rec[1])
                    if rec[2]:
                        id.append(rec[2])
                id = list(dict.fromkeys(id))

                mobile_token = ManagerParent.objects.filter(Q(parent_id__in=id), Q(db_name=school_name),
                                                            Q(is_active=True)).values_list('mobile_token').order_by(
                    '-pk')

                token = []

                for tok in mobile_token:
                    token.append(tok[0])

                push_service = FCMNotification(
                    api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                registration_id = token

                message_title = school_message[0][1] if school_message[0][1] else ''
                message_body = school_message[0][0] if school_message[0][0] else ''

                if message_title == 'Badge':
                    message_title = 'Badge'
                    message_body = 'A badge has been awarded to ' + student_name
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'أوسمة'
                                message_body = ' تم منح وسام للطالب ' + student_name
                        if registration_id:
                            registration_id = list(dict.fromkeys(registration_id))
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Badge",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3', message_title=message_title,
                            #                                            message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Badge","student_name":student_name})
                elif message_title == 'Weekly Plan':
                    message_title = 'Weekly Plan'
                    message_body = student_name + '  - A new weekly plan for the next week has been published'
                    cursor.execute(
                        "select  action_id,plan_name from message_student WHERE student_id = %s and school_message_id=%s",
                        [std, message_id])
                    action = cursor.fetchall()
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'الخطة الأسبوعية'
                                message_body = f'{student_name}  - تم نشر خطة أسبوعية جديدة للأسبوع القادم   '
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Weekly",
                                              "student_name": student_name, "action": str(action[0][0]),
                                              "plan_name": str(action[0][1])})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3', message_title=message_title,
                            #                                            message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Weekly","student_name":student_name,"action":str(action[0][0]),"plan_name":str(action[0][1])} )
                elif message_title == 'Assignment':
                    message_title = 'Online Assignment '
                    message_body = student_name + ' - ' + message_body
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = ' الواجبات الإلكترونية'
                                message_body = message_body.replace(student_name + ' - ', '')
                                # message_body=message_body.replace(student_name, '')
                                message_body = student_name + ' - ' + message_body
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Assignment",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3', message_title=message_title,
                            #                                            message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Assignment","student_name":student_name})
                elif message_title == 'Exam':
                    message_title = 'Online Exam '
                    message_body = student_name + ' - ' + message_body
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = '  الامتحانات الالكترونية'
                                message_body = message_body.replace(student_name + ' - ', '')
                                message_body = student_name + ' - ' + message_body
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Exam",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3', message_title=message_title,
                            #                                            message_body=message_body,data_message=
                            #                                               {"student_id":str(std),"picked":False,"model_name":"Exam","student_name":student_name} )
                elif message_title == 'Homework':
                    message_title = ' Homework'
                    message_body = student_name + ' - ' + message_body
                    cursor.execute(
                        "select  action_id from message_student WHERE student_id = %s and school_message_id=%s",
                        [std, message_id])
                    action = cursor.fetchall()
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()

                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_body = message_body.replace(student_name + ' - ', '')

                                message_title = ' الواجبات المنزلية '
                                message_body = student_name + ' - ' + message_body
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Homework",
                                              "student_name": student_name, "action": str(action[0][0])})
                        #     result = push_service.notify_multiple_devices(registration_ids=registration_id,
                        #                                                sound='new_beeb.mp3', message_title=message_title,
                        #                                                message_body=message_body,
                        # data_message={"student_id":str(std),"picked":False,"model_name":"Homework","student_name":student_name,"action":str(action[0][0])}  )
                elif message_title == 'Event':
                    message_title = 'School Event'
                    message_body = student_name + ' - ' + message_body
                    cursor.execute(
                        "select  action_id from message_student WHERE student_id = %s and school_message_id=%s",
                        [std, message_id])
                    action = cursor.fetchall()
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()

                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = ' الأنشطة المدرسية'
                                message_body = message_body.replace(student_name + ' - ', '')
                                message_body = student_name + ' - ' + message_body

                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Event",
                                              "student_name": student_name, "action": str(action[0][0])})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,sound='new_beeb.mp3',message_title=message_title,message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Event","student_name":student_name,"action":str(action[0][0])})
                elif message_title == 'Meeting':
                    message_title = 'Events'
                    message_body = message_body.replace(student_name + ' - ', '')
                    message_body = student_name + " " + message_body
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'المناسبات'
                                message_body = student_name + " - " + message_body
                        if registration_id:
                            for token in registration_id:
                                print(student_name)
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Meeting",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,sound='new_beeb.mp3',message_title=message_title,message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Meeting","student_name":student_name})
                elif message_title == 'Absence':
                    message_title = 'Absence Request'
                    message_body = ' Absence has been ' + 'Approved' if 'Approval' in message_body else 'Rejected for ' + student_name
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'Absence Request'
                                message_body = ' Absence has been ' + 'Approved' if 'Approval' in message_body else 'Rejected for ' + student_name
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Absence",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,sound='new_beeb.mp3',message_title=message_title,message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Absence","student_name":student_name})
                elif message_title == 'Mark':
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        message_title = 'Marks'
                        message_body += student_name
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'العلامات'

                                if "First Exam" in message_body:
                                    message_body = message_body.replace("First Exam", "التقويم الأول")
                                elif "Second Exam" in message_body:
                                    message_body = message_body.replace("Second Exam", "التقويم الثاني")
                                elif "Third Exam" in message_body:
                                    message_body = message_body.replace("Third Exam", "التقويم الثالث")
                                elif "Midterm Exam" in message_body:
                                    message_body = message_body.replace("Midterm Exam", "امتحان منتصف الفصل")
                                elif "Final Exam" in message_body:
                                    message_body = message_body.replace("Final Exam", "الامتحان النهائي")
                            else:
                                message_title = 'Marks'

                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Mark",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,sound='new_beeb.mp3',message_title=message_title,message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Mark","student_name":student_name})
                elif message_title == 'certification':
                    message_title = 'الشهادة المدرسية'
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'الشهادة المدرسية'
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3',
                            #                                            message_title=message_title,
                            #                                            message_body=message_body,
                            #                                            )
                elif message_title == 'daily_attendance':
                    st = 'Your Child ' + student_name
                    message_body = message_body.replace("Your Child", st)
                    if 'is late on' in message_body:
                        message_title = 'Late Notification'
                    elif 'is absent on' in message_body:
                        message_title = 'Absence Notification'
                        # st = 'Your Child ' + student_name
                        # message_body = message_body.replace("Your Child", st)
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'إشعار غياب'
                                if 'is late on' in message_body:

                                    message_body = f"   حضر الطالب  {student_name}   متأخرا   "
                                    message_title = ' إشعار تأخير'
                                elif 'is absent on' in message_body:
                                    message_body = ""
                                    message_body = f" الطالب   {student_name}  غائب  "
                                    message_title = 'إشعار غياب'
                                    # st = 'Your Child ' + student_name
                                    # message_body = message_body.replace("Your Child", st)
                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "Absence",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3',
                            #                                            message_title=message_title,
                            #                                            message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"Absence","student_name":student_name}
                            #                                            )
                elif message_title == 'clinic':
                    message_title = 'Clinic'
                    message_body += ' - ' + student_name
                    for parent_id in id:
                        cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                        parent = cursor.fetchall()
                        mobile_token_parent = ManagerParent.objects.filter(Q(parent_id=id), Q(db_name=school_name),
                                                                           Q(is_active=True)).values_list(
                            'mobile_token').order_by('-pk')
                        token_parent = []
                        for tok in mobile_token_parent:
                            token_parent.append(tok[0])
                            registration_id = token_parent
                        if parent[0][0]:
                            if 'en' not in parent[0][0]:
                                message_title = 'العيادة'

                        if registration_id:
                            for token in registration_id:
                                send_message(token, message_body, message_title,
                                             {"student_id": str(std), "picked": False, "model_name": "clinic",
                                              "student_name": student_name})
                            # result = push_service.notify_multiple_devices(registration_ids=registration_id,
                            #                                            sound='new_beeb.mp3', message_title=message_title,
                            #                                            message_body=message_body,data_message={"student_id":str(std),"picked":False,"model_name":"clinic","student_name":student_name})
                else:
                    for token in registration_id:
                        print("ddddddddddddddddddddddddddddddddddddddddddddddaaaaaaa")
                        send_message(token, message_body, message_title,
                                     {})

                    # result = push_service.notify_multiple_devices(message_title=message_title, message_body=message_body,
                    #                                               registration_ids=registration_id,
                    #                                               data_message={},sound='new_beeb.mp3',)

    return Response(result1)


@api_view(['POST'])
def send_confirmation_message_to_parent(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        student_name = request.data.get('student_name')
        student_id = request.data.get('student_id')
        parent_id = request.data.get('parent_id')

        # student_name=''
        mobile_token = ManagerParent.objects.filter(Q(parent_id=parent_id), Q(db_name=school_name),
                                                    Q(is_active=True)).values_list(
            'mobile_token').order_by('-pk')
        for e in mobile_token:
            mobile_token = e[0]
        # print("mmmmmmmmmmmmmmm",len(mobile_token),mobile_token)
        push_service = FCMNotification(
            api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
        # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
        registration_id = mobile_token

        message_title = "picked up"
        message_body = "please confirm that you have picked up  " + student_name + "from the school"
        # result = push_service.notify_single_device(registration_id=registration_id,
        #                                            message_title=message_title,
        #                                            message_body=message_body)
        # for token in registration_id:
        send_message(registration_id, message_body, message_title,
                     {"student_id": str(student_id), "picked": True})
        # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
        #                                            message_body=message_body,data_message={"student_id":str(student_id),"picked":True})
        # #
        # print(result)
        result1 = {
            "route": 'Ok'
        }

        return Response(result1)


@api_view(['POST'])
def send_dri(request):
    if request.method == 'POST':
        mobile_token = request.data.get('mobile_token')
        student_name = request.data.get('student_name')
        student_id = request.data.get('student_id')
        round_id = request.data.get('round_id')
        status = ''

        try:
            status = request.data.get('status')

            if mobile_token:
                # push_service = FCMNotification(
                #     api_key="AAAAXj2DTK0:APA91bFSxi4txQ8WffLYLBrxFVd3JMCSP5n9WfZafPnLpxC2i9cXHi2SofNoNSBgFWt2tgqjEstSeVkre-1FklyKn4NIy0AuYSwafkQt-RhXcVCth3RJdt8GUbTw9aZI70XFmYBshjuy")
                push_service = FCMNotification(
                    api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
                registration_id = mobile_token
                # registration_id = "dXBExPMQSpOQuPgw1alou8:APA91bEB8GZU9sTzQZlcZQbGr2Ssp_ZD66zSWzwYpvGJvBZCkpLPejq24GnNVtBeeO8KPQ1kisjrVrOgSuPI8jjNa45AlhV20lxLOq0cbVnnfXhAoi3f1S8KxBOiR-ErLicdiGz4g1yH"

                message_title = "Picked up by Parents"
                message_body = "The student " + student_name + " has been picked up by his parents, so please don't be waiting."
                if status:

                    status = 'in'
                else:
                    status = "absent"
                # for token in registration_id:
                send_message(registration_id, message_body, message_title,
                             {"json_data": json.dumps(
                                 {"student_id": student_id, "status": status,
                                  "student_name": student_name, "round_id": round_id,
                                  "date_time": ""})})
                # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                #                                            message_body=message_body, message_icon="",
                #                                            sound='new_beeb.mp3',
                #                                            data_message={"json_data": json.dumps(
                #                                                {"student_id": student_id, "status": status,
                #                                                 "student_name": student_name, "round_id": round_id,
                #                                                 "date_time": ""})}
                #                                            )
                # print(result)
                # mobile_token2=[]
                #
                # for e in mobile_token:
                #     mobile_token2.append(e[0])
                # if mobile_token2 and not ("token" in mobile_token2):
        except:
            status = ''
            # dFcb6UaVQAeAbMrAgnCF59:APA91bExNfxIYZF9QOZMHrp1bDABtihTkDc-8boLfqBvHIg76mlHv8zgEayFM3gT08YoMaeLTnwfGZKGCVNVd_x1zAbGFx4WjOE2_NTZGjRRT3s4clNxHk3XmJZdfvWl3beQDahHsFSc
            if mobile_token:
                # push_service = FCMNotification(
                #     api_key="AAAAXj2DTK0:APA91bFSxi4txQ8WffLYLBrxFVd3JMCSP5n9WfZafPnLpxC2i9cXHi2SofNoNSBgFWt2tgqjEstSeVkre-1FklyKn4NIy0AuYSwafkQt-RhXcVCth3RJdt8GUbTw9aZI70XFmYBshjuy")
                push_service = FCMNotification(
                    api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                # registration_id = "dXBExPMQSpOQuPgw1alou8:APA91bEB8GZU9sTzQZlcZQbGr2Ssp_ZD66zSWzwYpvGJvBZCkpLPejq24GnNVtBeeO8KPQ1kisjrVrOgSuPI8jjNa45AlhV20lxLOq0cbVnnfXhAoi3f1S8KxBOiR-ErLicdiGz4g1yH"
                registration_id = mobile_token

                message_title = "Picked up by Parents"
                message_body = "The student " + student_name + " has been picked up by his parents, so please don't be waiting."
                # for token in registration_id:
                send_message(registration_id, message_body, message_title,
                             {"json_data": json.dumps(
                                 {"student_id": student_id, "status": "absent",
                                  "student_name": student_name, "round_id": round_id,
                                  "date_time": ""})})
                # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                #                                            message_body=message_body, message_icon="",
                #                                            sound='new_beeb.mp3',
                #                                            data_message={"json_data": json.dumps(
                #                                                {"student_id": student_id, "status": "absent",
                #                                                 "student_name": student_name, "round_id": round_id,
                #                                                 "date_time": ""})}
                #                                            )
                # print(result)
                # mobile_token2=[]
                #
                # for e in mobile_token:
                #     mobile_token2.append(e[0])
                # if mobile_token2 and not ("token" in mobile_token2):

        signup_token = ''
        # with connections['tst'].cursor() as cursor:
        #     cursor.execute("select  driver_id from transport_round WHERE id = %s", [round_id])
        #     data_id_bus = cursor.fetchall()
        #     cursor.execute(
        #         "select token from public.res_partner  WHERE id=%s;",
        #         [data_id_bus[0][0]])
        #     signup_token = cursor.fetchall()
        # mobile_token = signup_token[0][0]

        result1 = {
            "route": 'Ok'
        }

        return Response(result1)


@api_view(['POST'])
def send_survey_message_to_parent(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        message_body = request.data.get('message')
        parent_id = request.data.get('parent_id')
        mobile_token = ManagerParent.objects.filter(Q(parent_id=parent_id), Q(db_name=school_name),
                                                    Q(is_active=True)).values_list(
            'mobile_token').order_by('-pk')
        for e in mobile_token:
            mobile_token = e[0]

        push_service = FCMNotification(
            api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
        # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
        registration_id = mobile_token

        message_title = "Survey"
        message_body = message_body
        send_message(registration_id, message_body, message_title,
                     {})
        # result = push_service.notify_single_device(registration_id=registration_id,sound='new_beeb.mp3', message_title=message_title,
        #                                            message_body=message_body,
        #                                            )
        # #
        # print(result)
        result1 = {
            "route": 'Ok'
        }

        return Response(result1)


@api_view(['POST'])
def push_notification(request):
    if request.method == 'POST':
        if request.headers:
            if request.headers.get('Authorization'):
                if 'Bearer' in request.headers.get('Authorization'):
                    au = request.headers.get('Authorization').replace('Bearer', '').strip()
                    db_name = Manager.objects.filter(token=au).values_list('db_name')
                    driver_id = Manager.objects.filter(token=au).values_list('driver_id')
                    if db_name:
                        for e in db_name:
                            school_name = e[0]
                            school_name = Manager.pincode(school_name)
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
                            parent_id = request.data.get('parent_id')
                            mobile_token = []
                            # school_name = ManagerParent.objects.filter(school_id=school_id).values_list('db_name').order_by('-pk')
                            # school_name=school_name[0][0]

                            # for rec in parent_id:

                            with connections[str(school_name)].cursor() as cursor:
                                if user_id != 0:
                                    cursor.execute(
                                        "select  father_id,mother_id,responsible_id_value from student_student WHERE id= %s",
                                        [user_id])
                                    student_info = cursor.fetchall()
                                    if student_info:
                                        for rec in student_info[0]:

                                            cursor.execute("select  settings from school_parent WHERE id = %s", [rec])
                                            settings = cursor.fetchall()
                                            mobile_token1 = ManagerParent.objects.filter(Q(parent_id=rec),
                                                                                         Q(db_name=school_name),
                                                                                         Q(is_active=True)).values_list(
                                                'mobile_token').order_by('-pk')
                                            if settings:
                                                if settings[0] != 'None' and str(settings[0][0]) != 'None':
                                                    data = json.loads(settings[0][0])
                                                    for e in mobile_token1:
                                                        notifications = {"locale": 'en',
                                                                         "nearby": True,
                                                                         "check_in": True,
                                                                         "check_out": True}
                                                        if type(data['notifications']) is str:
                                                            li = list(data['notifications'].split(","))
                                                            notifications = {

                                                                "locale": "ar" if "ar" in li[3] else 'en',
                                                                "nearby": True if "true" in li[0] else False,
                                                                "check_in": True if "true" in li[1] else False,
                                                                "check_out": True if "true" in li[2] else False

                                                            }
                                                        elif type(data['notifications']) is dict:
                                                            try:
                                                                notifications = {

                                                                    "locale": data['notifications']['locale'],
                                                                    "nearby": data['notifications']['nearby'],
                                                                    "check_in": data['notifications']['check_in'],
                                                                    "check_out": data['notifications']['check_out']

                                                                }
                                                            except:

                                                                notifications = {"locale": 'en',
                                                                                 "nearby": True,
                                                                                 "check_in": True,
                                                                                 "check_out": True}
                                                        # notifications = json.loads(str(data['notifications']))

                                                        # print(type(notifications))
                                                        if notifications['nearby'] and (
                                                                action == 'near' or action == 'driver'):
                                                            mobile_token.append(e[0])
                                                        elif notifications['check_in'] and (
                                                                action == 'near' or action == 'driver'):
                                                            mobile_token.append(e[0])
                                                        elif notifications['check_out'] and (
                                                                action == 'near' or action == 'driver'):
                                                            mobile_token.append(e[0])
                                                        else:
                                                            mobile_token.append(e[0])
                                            else:

                                                for e in mobile_token1:
                                                    mobile_token.append(e[0])
                                            if mobile_token1:
                                                push_service = FCMNotification(
                                                    api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                                # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
                                                registration_id = mobile_token1[0][0]
                                                message_title = title
                                                message_body = message
                                                send_message(registration_id, message_body, message_title,
                                                             {})

                                                # result = push_service.notify_single_device(registration_id=registration_id,
                                                #                                            message_title=message_title,
                                                #                                            message_body=message_body,sound='new_beeb.mp3')

                                                result1 = {
                                                    "route": 'Ok'
                                                }
                                                return Response(result1)
                                    result1 = {
                                        "route": 'Ok111'
                                    }
                                    return Response(result1)

                                    # if settings:
                                    #     parent_id=settings[0][1]
                                else:
                                    cursor.execute("select  settings from school_parent WHERE id = %s", [parent_id])
                                    settings = cursor.fetchall()

                                mobile_token1 = ManagerParent.objects.filter(Q(parent_id=parent_id),
                                                                             Q(db_name=school_name),
                                                                             Q(is_active=True)).values_list(
                                    'mobile_token').order_by('-pk')

                            # print(rec,school_id, ManagerParent.objects.filter(Q(user_id=rec) , Q(db_name=school_name),Q(is_active=True)).values_list(
                            #     'mobile_token').order_by('-pk'))

                            if settings:
                                if settings[0] == 'None':
                                    data = json.loads(settings[0][0])
                                    for e in mobile_token1:
                                        if data['notifications']['nearby'] and (action == 'near' or action == 'driver'):
                                            mobile_token.append(e[0])
                                        elif data['notifications']['check_in'] and (
                                                action == 'near' or action == 'driver'):
                                            mobile_token.append(e[0])
                                        elif data['notifications']['check_out'] and (
                                                action == 'near' or action == 'driver'):
                                            mobile_token.append(e[0])
                                        else:
                                            mobile_token.append(e[0])
                                for e in mobile_token1:
                                    mobile_token.append(e[0])
                                if mobile_token:
                                    push_service = FCMNotification(
                                        api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                    # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
                                    registration_id = mobile_token
                                    message_title = title
                                    message_body = message
                                    send_message(registration_id, message_body, message_title,
                                                 {})
                                    # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                    #                                            message_body=message_body)
                                    result1 = {
                                        "route": 'Ok'
                                    }
                                    return Response(result1)

                            else:
                                for e in mobile_token1:
                                    mobile_token.append(e[0])
                                    # for e in mobile_token:
                                    #     mobile_token = e[0]
                                    # print("mmmmmmmmmmmmmmm",len(mobile_token),mobile_token)
                                    push_service = FCMNotification(
                                        api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
                                    # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
                                    if mobile_token:
                                        registration_id = mobile_token[0]
                                        message_title = title
                                        message_body = message
                                        send_message(registration_id, message_body, message_title,
                                                     {})
                                        # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                        #                                            message_body=message_body,sound='new_beeb.mp3')
                                        result1 = {
                                            "route": 'Ok'
                                        }

                                        return Response(result1)
                            result1 = {
                                "route": 'Ok'
                            }
                            return Response(result1)


@api_view(['POST', 'GET'])
def test_lis(request):
    if request.method == 'POST':
        # school_name = request.data.get('school_name')
        print(request.data)

        manager = ManagerTracker(data_api=request.data)
        manager.save()
        result1 = {
            "route": 'successful'
        }
        return Response(result1)
    elif request.method == 'GET':
        manager = ManagerTracker(data_api='unique_id')
        manager.save()
        result1 = {
            "route": 'successful'
        }

        return Response(result1)


@api_view(['POST', 'GET'])
def send_chat_parent(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        message_body = ''
        message_id = request.data.get('message_id')
        parent_id = request.data.get('parent_id')
        f_id = request.data.get('f_id')
        m_id = request.data.get('m_id')
        student_id = request.data.get('student_id')
        student_name = ''
        # print(school_name)

        # with connections[school_name].cursor() as cursor:
        #     cursor.execute(
        #         "select  display_name_search from student_student WHERE  id = %s  And state = 'done'",
        #         [student_id])
        #     student = cursor.fetchall()
        #     student_name=student[0][0]
        #     cursor.execute(
        #         "select  body from mail_message WHERE  id = %s ",
        #         [message_id])
        #     message = cursor.fetchall()
        #     print(message)
        #     message_body =message[0][0]
        #     print(message_body)

        mobile_token_g = ManagerParent.objects.filter(Q(parent_id=parent_id), Q(db_name=school_name),
                                                      Q(is_active=True)).values_list(
            'mobile_token').order_by('-pk')
        mobile_token_f = ManagerParent.objects.filter(Q(parent_id=f_id), Q(db_name=school_name),
                                                      Q(is_active=True)).values_list(
            'mobile_token').order_by('-pk')
        mobile_token_m = ManagerParent.objects.filter(Q(parent_id=m_id), Q(db_name=school_name),
                                                      Q(is_active=True)).values_list(
            'mobile_token').order_by('-pk')
        mobile_token = []
        for e in mobile_token_g:
            mobile_token_g = e[0]
            mobile_token.append(e[0])
        for e in mobile_token_m:
            mobile_token_m = e[0]
            mobile_token.append(e[0])
        for e in mobile_token_f:
            mobile_token_f = e[0]
            mobile_token.append(e[0])
        r = Timer(3.0, twoArgsChat, (message_id, school_name, mobile_token, student_id))
        r.start()
        # push_service = FCMNotification(api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
        # if mobile_token_g:
        #     registration_id = mobile_token_g
        #     message_title = student_name
        #     message_body = message_body
        #
        #     result = push_service.notify_single_device(registration_id=registration_id,sound='new_beeb.mp3', message_title=message_title,
        #                                                message_body=message_body,
        #                                                )
        # if mobile_token_m:
        #     registration_id = mobile_token_m
        #     message_title =  student_name
        #     message_body = message_body
        #
        #     result = push_service.notify_single_device(registration_id=registration_id, sound='new_beeb.mp3',
        #                                                message_title=message_title,
        #                                                message_body=message_body,
        #                                                )
        # if mobile_token_f:
        #     registration_id = mobile_token_f
        #     message_title = student_name
        #     message_body = message_body
        #
        #     result = push_service.notify_single_device(registration_id=registration_id, sound='new_beeb.mp3',
        #                                                message_title=message_title,
        #                                                message_body=message_body,
        #                                                )
        result1 = {
            "route": 'Ok'
        }
        #
        return Response(result1)


def twoArgsChat(message_id, school_name, mobile_token, student_id):
    with connections[school_name].cursor() as cursor:
        cursor.execute(
            "select  display_name_search from student_student WHERE  id = %s  And state = 'done'",
            [student_id])
        student = cursor.fetchall()
        student_name = student[0][0]
        cursor.execute(
            "select  body from mail_message WHERE  id = %s ",
            [message_id])
        message = cursor.fetchall()
        patterns = re.compile('<.*?>')
        message_body = message[0][0]
        message_body = re.sub(patterns, '', message_body)
        mobile_token = list(dict.fromkeys(mobile_token))
        push_service = FCMNotification(
            api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
        for mobile in mobile_token:
            registration_id = mobile
            message_title = student_name
            message_body = message_body
            send_message(registration_id, message_body, message_title,
                         {"student_id": str(student_id),
                          "picked": False, "model_name": "Chat", "student_name": student_name})
            # result = push_service.notify_single_device(registration_id=registration_id, sound='new_beeb.mp3',
            #                                            message_title=message_title,
            #                                            message_body=message_body,data_message={"student_id":str(student_id),
            #                                                                                    "picked":False,"model_name":"Chat","student_name":student_name}
            #                                            )
        result1 = {
            "route": 'Ok'

        }

        return Response(result1)