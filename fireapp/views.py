from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyrebase
from datetime import date

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
