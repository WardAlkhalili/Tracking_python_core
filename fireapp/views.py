from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyrebase
from datetime import date
from pyfcm import FCMNotification
from django.db import connections
from Parent_api.models import ManagerParent
from Driver_api.models import Manager

from django.db.models import Q
from datetime import datetime
import calendar
import json
from threading import Timer
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


@api_view(['GET'])
def Get_last_bus_location(request, bus_id, school_name):
    if request.method == 'GET':
        fullRound = school_name + "-stg-round-" + str(bus_id)
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

        r =Timer(3.0, twoArgs, (message_id, school_name))
        r.start()
        result1 = {
            "route": 'Ok'

        }

    return Response(result1)




def twoArgs(message_id,school_name):
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
                "select  mother_id,father_id,responsible_id_value from student_student WHERE id = %s ",
                [std])
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
            id = list(dict.fromkeys(id))


            # cursor.execute(
            #     "select  user_id from school_parent WHERE id in %s ",
            #     [tuple(id)])
            # columns = (x.name for x in cursor.description)
            # parent = cursor.fetchall()
            # parent_id = []
            # for rec in parent:
            #     parent_id.append(rec[0])
            #
            mobile_token = ManagerParent.objects.filter(Q(parent_id__in=id), Q(db_name=school_name),
                                                        Q(is_active=True)).values_list(
                'mobile_token').order_by('-pk')

            token = []

            for tok in mobile_token:

                token.append(tok[0])
            # print("ffffffffff",len(token))

            push_service = FCMNotification(
                api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
            registration_id = token



            message_title = school_message[0][1]
            # print(message_title)
            message_body = school_message[0][0]
            result = push_service.notify_multiple_devices(message_title=message_title, message_body=message_body,
                                                          registration_ids=registration_id,
                                                          data_message={})






        result1 = {
            "route": 'Ok'

        }

    return Response(result1)


@api_view(['POST'])
def send_confirmation_message_to_parent(request):
    if request.method == 'POST':
        school_name = request.data.get('school_name')
        student_name = request.data.get('student_name')
        student_id=request.data.get('student_id')
        parent_id = request.data.get('parent_id')

        # student_name=''
        mobile_token = ManagerParent.objects.filter(Q(parent_id=parent_id) , Q(db_name=school_name),Q(is_active=True)).values_list(
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
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body,data_message={"student_id":str(student_id),"picked":True})
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
        if mobile_token:
            push_service = FCMNotification(
                api_key="AAAAzysR6fk:APA91bFX6siqzUm-MQdhOWlno2PCOMfFVFIHmcfzRwmStaQYnUUJfDZBkC2kd2_s-4pk0o5jxrK9RsNiQnm6h52pzxDbfLijhXowIvVL2ReK7Y0FdZAYzmRekWTtOwsyG4au7xlRz1zD")
            # registration_id = "fw7CryLaRjW8TEKOyspKLo:APA91bFQYaCp4MYes5BIQtHFkOQtcPdtVLB0e5BJ-dQKE2WeYBeZ3XSmNpgWJX-veRO_35lOuGzTm6QBv1c2YZM-4WcT1drKBvLdJxEFkhG5l5c-Af_IRtCJzOOKf7c5SmEzzyvoBrQx"
            registration_id = mobile_token

            message_title = "Picked up with Parents"
            message_body = "The student "+student_name+" has been picked up by their parents, so please don't wait for them."

            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                       message_body=message_body, message_icon="",
                                                       data_message={"json_data": json.dumps(
                                                           {"student_id": student_id, "status": "absent",
                                                            "student_name": student_name, "round_id": round_id,
                                                            "date_time": ""})}
                                                       )
            # mobile_token2=[]
            #
            # for e in mobile_token:
            #     mobile_token2.append(e[0])
            # if mobile_token2 and not ("token" in mobile_token2):




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

        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body,
                                                   )
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
                            school_name = ManagerParent.objects.filter(school_id=school_id).values_list('db_name').order_by('-pk')
                            # print(school_name[0][0])
                            school_name=school_name[0][0]

                            # for rec in parent_id:

                            with connections[str(school_name)].cursor() as cursor:
                                    if  user_id != 0:
                                        cursor.execute("select  father_id,mother_id,responsible_id_value from student_student WHERE id= %s",
                                                       [user_id])
                                        student_info = cursor.fetchall()
                                        if student_info:
                                            for rec in student_info[0]:


                                                cursor.execute("select  settings from school_parent WHERE id = %s", [rec])
                                                settings = cursor.fetchall()
                                                mobile_token1 = ManagerParent.objects.filter(Q(parent_id=rec), Q(db_name=school_name),Q(is_active=True)).values_list('mobile_token').order_by('-pk')
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

                                                    result = push_service.notify_single_device(registration_id=registration_id,
                                                                                               message_title=message_title,
                                                                                               message_body=message_body)

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

                                    mobile_token1 = ManagerParent.objects.filter(Q(parent_id=parent_id), Q(db_name=school_name),
                                                                                 Q(is_active=True)).values_list(
                                        'mobile_token').order_by('-pk')


                                # print(rec,school_id, ManagerParent.objects.filter(Q(user_id=rec) , Q(db_name=school_name),Q(is_active=True)).values_list(
                                #     'mobile_token').order_by('-pk'))

                            if settings:
                                if settings[0]=='None':
                                    data = json.loads(settings[0][0])
                                    for e in mobile_token1:
                                        if data['notifications']['nearby'] and (action =='near' or action =='driver'):
                                            mobile_token.append(e[0])
                                        elif    data['notifications']['check_in'] and (action =='near' or action =='driver'):
                                            mobile_token.append(e[0])
                                        elif data['notifications']['check_out'] and (action =='near' or action =='driver'):
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
                                    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                                               message_body=message_body)
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
                                        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                                                   message_body=message_body)
                                        result1 = {
                                            "route": 'Ok'
                                        }

                                        return Response(result1)
                            result1 = {
                                "route": 'Ok'
                            }
                            return Response(result1)
