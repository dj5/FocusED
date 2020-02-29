import cv2
import os
import pyrebase
import numpy as np
from PIL import Image
from django.shortcuts import render, redirect
from django.contrib import messages

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
#Getting reference to Firebase Database
fb_db = firebase.database()
fb_auth = firebase.auth()

#Function used in training faces model
def getImagesWithID(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # print image_path
    #getImagesWithID(path)
    faces = []
    IDs = []
    for imagePath in imagePaths:
        # Read the image and convert to grayscale
        if imagePath == "/home/atharva/sihackathon/capture/facesData/Thumbs.db" :
            continue
        facesImg = Image.open(imagePath).convert('L')
        faceNP = np.array(facesImg, 'uint8')
        # Get the label of the image
        ID = np.long(os.path.split(imagePath)[-1].split(".")[1])
        #ID= str(os.path.split(imagePath)[-1].split(".")[1])
         # Detect the face in the image
        faces.append(faceNP)
        IDs.append(ID)
        #print(IDs)
        #cv2.imshow("Adding faces for traning",faceNP)
        #cv2.waitKey(10)
    return np.array(IDs), faces


# Create your views here.
def index(request):
    return render(request,'index.html')


def capture(request):
    if request.method == 'POST':

        roll = int(request.POST['roll'])
        existing_roll = fb_db.child('student').order_by_child('Roll').equal_to(roll).get()
        #print(existing_roll.val())
        flag = False
        try:
            if existing_roll.val():
                flag = True
        except:
            print("Null")

        # if roll no already exists do not capture images, return error
        if flag:
            messages.info(request, 'Roll No. already exists')
            return render(request, 'capture.html')
        #else capture images and store it in facesData
        else:
            #Capturing Images
            face_cascade = cv2.CascadeClassifier('/home/atharva/sihackathon/capture/haarcascade_frontalface_default.xml')
            cap = cv2.VideoCapture(0)
            id = roll
            sampleN = 0
            while 1:
                ret, img = cap.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    sampleN = sampleN + 1
                    cv2.imwrite("/home/atharva/sihackathon/capture/facesData/User." + str(id) + "." + str(sampleN) + ".jpg",gray[y:y + h, x:x + w])
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.waitKey(100)
                cv2.imshow('img', img)
                cv2.waitKey(1)
                if sampleN > 29:
                    break
            cap.release()
            cv2.destroyAllWindows()
            #Training the model
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            path = "/home/atharva/sihackathon/capture/facesData"
            Ids, faces = getImagesWithID(path)
            recognizer.train(faces, Ids)
            recognizer.save("/home/atharva/sihackathon/capture/trainingdata.yml")
            #cv2.destroyAllWindows()
            #Returning Response
            messages.info(request, 'New Student Face Captured Successfully!')
            return redirect('/')

    else:
        return render(request,'capture.html')


def login(request):
    #If already logged-in and trying to access login page
    if request.session.has_key('uid'):
        return redirect('/StudDashBoard')
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
            return redirect('/StudDashBoard')
        except:
            #flag = True
            messages.error(request, 'Invalid Credentials')
            return render(request, 'login.html')
    #Else display normal login page
    else:
        return render(request,'login.html')

def StudDashBoard(request):
    return render(request, 'stud_login.html')
