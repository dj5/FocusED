from collections import OrderedDict
from operator import getitem
import json
import random
import cv2
import csv
import pyrebase
import time
from datetime import datetime, timezone
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import pandas as pd

def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote
#Firebase Configuration
config = {
    "apiKey": "AIzaSyArY1eRDVcvfpKs6qmtmt7W4QiRamXoDeQ",
    "authDomain": "sih2020-39a8a.firebaseapp.com",
    "databaseURL": "https://sih2020-39a8a.firebaseio.com",
    "projectId": "sih2020-39a8a",
    "storageBucket": "sih2020-39a8a.appspot.com",
    "messagingSenderId": "355658314171",
    "appId": "1:355658314171:web:958625b62f8945b7be949e"
}
#Initializing Firebase with Configs
firebase = pyrebase.initialize_app(config)
#Getting reference to Firebase Auth
fb_auth = firebase.auth()
fb_db = firebase.database()

#Capture Attendance
def mark_att():
    #Capturing Live Video
    face_cascade = cv2.CascadeClassifier('/home/atharva/sihackathon/capture/haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    #Creating face Recognizer
    rec = cv2.face.LBPHFaceRecognizer_create()
    #Reading the training data
    rec.read('/home/atharva/sihackathon/capture/trainingdata.yml')
    id = None
    ids = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    #Capture Live video for some seconds 10,15...
    #t_end = time.time() + 20
    #while time.time() < t_end:
    while 1:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.5, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            id, conf = rec.predict(gray[y:y + h, x:x + w])
            ids.append(id)
            cv2.putText(img, str(id), (x, y + h), font, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('img',img)
        if cv2.waitKey(1) == ord('q'):
            break

    ids = list(dict.fromkeys(ids))
    fields = ['roll']
    rows = []
    for x in ids:
        rows.append([x])
    print(rows)
    filename = "session_id.csv"
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

    cap.release()
    cv2.destroyAllWindows()

# Create your views here.
@csrf_exempt
def attendance(request):
    if not request.session.has_key('uid'):
        return redirect('/faculty')

    if request.session.has_key('lec_session_id'):
        mark_att()
        #messages.success(request,'Attendance Captured Successfully!')
        return redirect('/faculty/dashboard')
    else:
        messages.error(request, 'Lecture is not started')
        return redirect('/faculty/dashboard')


@csrf_exempt
def getAvgAttentiveness(request):
    if not request.session.has_key('uid'):
        return redirect('/faculty')

    if request.session.has_key('lec_session_id'):
        session = request.session['lec_session_id']
        #print(session['name'])
        try:
            res = fb_db.child('avg-attentiveness').order_by_child('session').equal_to(session['name']).get()
            dict_org = res.val()
            dict_ord = OrderedDict(sorted(dict_org.items(),key=lambda x: getitem(x[1], 'dt'),reverse=True))
            attentiveness = list(dict_ord.values())[0]['attentiveness']
            date = list(dict_ord.values())[0]['dt']
            #print(date)
            data = {
                'attentiveness': attentiveness,
                'dt' : date
            }
            return JsonResponse(data)
        except:
            data = {}
            return JsonResponse(data)
        #print(res.val())

    else:
        messages.error(request, 'Lecture is not started')
        return redirect('/faculty/dashboard')


@csrf_exempt
def getStdAttentiveness(request):
    if not request.session.has_key('uid'):
        return redirect('/faculty')

    if request.session.has_key('lec_session_id'):
        session = request.session['lec_session_id']
        #print(session['name'])
        data = []
        try:

            data = []
            res = fb_db.child('student-wise-att').order_by_child('session').equal_to(session['name']).get()
            dict_org = res.val()
            dict_ord = OrderedDict(sorted(dict_org.items(),key=lambda x: getitem(x[1], 'Roll')))
            for x in dict_ord.values():
                temp = {
                    'Name' : x['Name'],
                    'Roll': x['Roll'],
                    'attentiveness' : x['attentiveness']
                }
                data.append(temp)


            #print(data)
            return JsonResponse(data,safe=False)


        except:
            return JsonResponse(data, safe=False)

    else:
        messages.error(request, 'Lecture is not started')
        return redirect('/faculty/dashboard')


@csrf_exempt
def dummyRecordIns(request):
    update_dt = datetime.now()
    data = {}
    attentiveness = random.randrange(30, 90, 3)
    try:
        #fb_db.child("avg-attentiveness").child("random").update({"dt": update_dt.strftime("%d/%m/%Y %H:%M:%S")})
        #fb_db.child("avg-attentiveness").child("random").update({"attentiveness": attentiveness})
        #fb_db.child("student-wise-att").child("random").update({'attentiveness': random.randrange(30, 90, 3)})
        #fb_db.child("student-wise-att").child("random1").update({'attentiveness': random.randrange(30, 90, 3)})
        return JsonResponse(data)
    except:
        return JsonResponse(data)

@csrf_exempt
def notifications(request):
    if request.session.has_key('uid'):
        data = []

        res = fb_db.child('notifications').order_by_child('dped').equal_to(0).get()
        print(res)
        dict_org = res.val()
        #dict_ord = OrderedDict(sorted(dict_org.items(), key=lambda x: getitem(x[1], 'Roll')))
        for x in dict_org.values():
            temp = {
                'Roll': x['Roll'],
                'Description': x['Desc']
            }
            data.append(temp)
        #print(data)
        fb_db.child("notifications").child("random").update({"dped": 1})
        fb_db.child("notifications").child("random1").update({"dped": 1})
        fb_db.child("notifications").child("random2").update({"dped": 1})
        fb_db.child("notifications").child("random3").update({"dped": 1})
        return JsonResponse(data, safe=False)
    else:
        return redirect('/faculty')


def login(request):
    #If already logged-in and trying to access login page
    if request.session.has_key('uid'):
        return redirect('/faculty/dashboard')
    #If form is submitted perfrom:
    if request.method == 'POST':
        #Getting email and password from user-submiteed form (login.html)
        email = request.POST['email']
        password = request.POST['password']
        #Authenticating the user
        #flag = False
        try:
            user = fb_auth.sign_in_with_email_and_password(email,password)
            print(user)
            request.session['uid'] = str(user['localId'])
            request.session['refreshToken'] = str(user['refreshToken'])
            request.session['uemail'] = str(user['email'])
            return redirect('/faculty/dashboard')
        except:
            #flag = True
            messages.error(request, 'Invalid Credentials')
            return render(request, 'login.html')
    #Else display normal login page
    else:
        return render(request,'login.html')


def logout(request):

    #Remove the session uid and recirect to login page
    request.session.pop('uid')
    request.session.flush()
    return redirect('/faculty')


def dashboard(request):

    #Check for session
    if request.session.has_key('uid'):
        #Refreshing Session evertime dashboard is reloaded to avoid session expiry
        user = fb_auth.refresh(request.session['refreshToken'])
        #print(user)
        request.session['uid'] = str(user['userId'])
        request.session['refreshToken'] = str(user['refreshToken'])

        #If form submitted
        if request.method == 'POST':
            #if lec start clicked
            print('Post cha aat ala')
            if request.POST.get('start',False):
                print('start called')
                #Store details into db
                lec_id = request.POST['lec_id'].upper()
                res = fb_db.child("lecture").child(lec_id).get()
                #if LEC_ID is there, do:
                if(res.val()):
                    start_dt = datetime.now()
                    # print(start_dt.strftime("%d %B %Y %H %M %S"))
                    # Getting FAC_ID from database, get() returns response object,
                    # val() returns ordered dictionary
                    # get() returns value of specified key
                    fac_id_od = fb_db.child('faculty').child(request.session['uid']).get()
                    print("before datyaaaa",request.session['uid'])
                    try:
                        print("Try cha aat ala",fac_id_od.val())
                        data = {
                            'fac_id': fac_id_od.val().get('fac_id'),
                            'lec_id': lec_id,
                            'start_dt': start_dt.strftime("%d/%m/%Y %H:%M:%S"),
                            'end_dt': ''
                        }
                        # Pushing data to databse, it will return random-generated value (here session's child for which data is pushed)
                        print("before session")
                        request.session['lec_session_id'] = fb_db.child('session').push(data)
                        print("after session")
                        # print(request.session['lec_session_id']['name']) key-> value pair is returned so to access value
                        # print(request.session['lec_session_id']) to access in json form
                        messages.success(request, 'Lecture is started..')
                        # to hide start and display stop on dashboard, passing session id as parameter to response
                        return render(request, 'dashboard.html',
                                      {'isStarted': request.session['lec_session_id']['name']})
                    except:
                        messages.error(request, 'Some error occured, try again later')
                        # if session is not started, it should again display Start button so keep isStarted empty
                        return render(request, 'dashboard.html', {'isStarted': ''})
                # if LEC_ID is not found, display error msg!
                else:
                    messages.error(request, 'Invalid Lecture ID')
                    return render(request, 'dashboard.html', {'isStarted': ''})


            # if lec stop clicked
            if request.POST.get('stop',False):
                #update end_dt in database
                end_dt = datetime.now()
                try:
                    data = {
                        'end_dt':end_dt.strftime("%d/%m/%Y %H:%M:%S")
                    }
                    #add session end date_time to existing session doc in database
                    fb_db.child('session').child(request.session['lec_session_id']['name']).update(data)
                    request.session.pop('lec_session_id')
                    messages.success(request,'Lecture is stopped..')
                    #display stop button, so pass isStarted as empty
                    return render(request, 'dashboard.html', {'isStarted': ''})

                except:
                    messages.error(request, 'Some error occured, try again later')
                    return render(request, 'dashboard.html', {'isStarted': request.session['lec_session_id']['name']})


        else:
            #if it is normal page refresh request then
            try:
                #we can also use if..else but nesting would be toooo much
                #if session is already started display stop
                return render(request, 'dashboard.html', {'isStarted': request.session['lec_session_id']['name'] })
            except:
                #else display start
                return render(request, 'dashboard.html', {'isStarted':'' })


    #if not logged in, redirect to login page
    else:
        return redirect('/faculty')




def forgot(request):

    # If already logged-in and trying to access forgot page
    if request.session.has_key('uid'):
        return redirect('/faculty/dashboard')

    # If form is submited do:
    if request.method == 'POST':
        email = request.POST['email']
        try:
            #send pw reset e-mail
            fb_auth.send_password_reset_email(email)
            messages.success(request, 'A link to reset the password is sent to your e-mail')
            return redirect('/faculty')
        except:
            messages.error(request, 'Invalid Credentials')
            return render(request, 'forgot.html')
    #else display normal forgot page
    else:
        return render(request,'forgot.html')


def statistics(request):
    if request.session.has_key('uid'):
        return render(request,'statistics.html')
    else:
        return redirect('/faculty')

def cards(request):
    if request.session.has_key('uid'):
        return render(request,'cards.html')
    else:
        return redirect('/faculty')

def student_overview(request):
    if request.session.has_key('uid'):
        return render(request,'student_overview.html')
    else:
        return redirect('/faculty')

def student_attentiveness(request):
    if request.session.has_key('uid'):
        return render(request,'student_attentiveness.html')
    else:
        return redirect('/faculty')

def settings(request):
    #If logged in only
    if request.session.has_key('uid'):
        #Form submitted?
        if request.method == 'POST':
            try:
                # send pw reset e-mail
                email = request.session['uemail']
                fb_auth.send_password_reset_email(email)
                messages.success(request, 'A link to reset the password is sent to your e-mail')
                return redirect('/faculty/dashboard')
            except:
                messages.error(request, 'Some error occured, try again later')
                return redirect('/faculty/dashboard')

        else:
            return render(request, 'settings.html')

    else:
        return redirect('/faculty')

@csrf_exempt
def create_post(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data.csv")
        atten= int(df['Score'])
        green= int(df['green'])
        yellow= int(df['yellow'])
        red= int(df['red'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(str(atten))
        response_data['score'] = str(atten)
        response_data['green'] = str(green)
        response_data['yellow'] = str(yellow)
        response_data['red'] = str(red)
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def create_post_room(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data.csv")
        atten= int(df['Score'])
        green= int(df['green'])
        yellow= int(df['yellow'])
        red= int(df['red'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(str(atten))
        response_data['score'] = str(atten)
        response_data['green'] = str(green)
        response_data['yellow'] = str(yellow)
        response_data['red'] = str(red)
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def create_post_Attentiveness(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data_Attentive.csv")
        atten= int(df['Score'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(str(atten))
        response_data['score'] = str(atten)
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def create_post_Interaction(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data_Interaction.csv")
        atten= int(df['Score'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(str(atten))
        response_data['score'] = str(atten)
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def create_post_Emotion(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data_Emotion.csv")
        atten= int(df['Score'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(str(atten))
        response_data['score'] = str(atten)
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def create_post_Total(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data_Total.csv")
        atten= int(df['Score'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(str(atten))
        response_data['score'] = str(atten)
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def create_post_BarChart(request):

    if request.method == 'POST':
        print("ac")
        post_text = request.POST.get('the_post')
        response_data = {}
        df=pd.read_csv("/home/atharva/sihackathon/data_BarChart.csv")
        label = list(df['Label'])
        data = list(df['Data'])
      #  post = Post(text=post_text, author=request.user)
       # post.save()
        print(label)
        print(data)
        response_data['label'] = label
        response_data['data'] = data
        # response_data['postpk'] = post.pk
        # response_data['text'] = post.text
        # response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
        # response_data['author'] = post.author.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )