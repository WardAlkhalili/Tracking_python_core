from django.shortcuts import render
import pyrebase

# Remember the code we copied from Firebase.
#This can be copied by clicking on the settings icon > project settings, then scroll down in your firebase dashboard

config = {
    "apiKey": "AIzaSyB8q0kDZEevxxBpsbQwLNOKky66nyGE34c",
    "authDomain": "trackware-system.firebaseapp.com",
    "databaseURL": "https://trackware-system-default-rtdb.firebaseio.com",
    "projectId": "trackware-system",
    "storageBucket": "trackware-system.appspot.com",
    "messagingSenderId": "982679224932",
    "appId": "1:982679224932:web:38c0e5f6a00fa813c7d571"
}

#here we are doing firebase authentication
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()


def index(request):

    #accessing our firebase data and storing it in a variable
    name = database.child('Data').child('name').get().val()
    age = database.child('Data').child('age').get().val()
    gender = database.child('Data').child('gender').get().val()

    context = {
        'name':name,
        'age':age,
        'gender':gender
    }
    return render(request, 'index.html', context)
