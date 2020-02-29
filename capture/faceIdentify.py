import cv2
import csv
import time

t_end = time.time() + 20



face_cascade = cv2.CascadeClassifier('/home/atharva/sihackathon/capture/haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("/home/atharva/sihackathon/capture/trainingdata.yml")
id= None
ids = []
font = cv2.FONT_HERSHEY_SIMPLEX
while time.time() < t_end:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.5, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        id,conf=rec.predict(gray[y:y+h,x:x+w])
        ids.append(id)
        #cv2.cv.PutText(cv2.cv.fromarray(img),str(id),(x,y+h),font,255)
        cv2.putText(img,str(id),(x,y+h),font,0.75,(255,255,255),2,cv2.LINE_AA)

    #cv2.imshow('img',img)
    #if cv2.waitKey(1) == ord('q'):
        #break

ids = list(dict.fromkeys(ids))
fields = ['roll']
rows = []
for x in ids:
    rows.append([x])
print(rows)
filename = "session_id.csv"
with open(filename,'w',newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)

cap.release()
cv2.destroyAllWindows()
