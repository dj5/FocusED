from keras.engine import Model
from keras import models
from keras import layers
from keras.layers import Input
from keras.preprocessing import image
from keras_vggface.vggface import VGGFace
import numpy as np
from keras_vggface import utils
from scipy import spatial
import cv2
import pandas as pd
import os
import glob
import pickle
import mix5
from WebcamThread import WebcamVideoStream
from AttenThread import AttenThread
import tensorflow as tf
import time
from keras import backend as K
K.clear_session()
graph = tf.get_default_graph()
import pyrebase
config = {
  "apiKey": "AIzaSyArY1eRDVcvfpKs6qmtmt7W4QiRamXoDeQ",
  "authDomain": "sih2020-39a8a.firebaseapp.com",
  "databaseURL": "https://sih2020-39a8a.firebaseio.com",
  "projectId": "sih2020-39a8a",
  "storageBucket": "sih2020-39a8a.appspot.com",
  "messagingSenderId": "355658314171",
  "appId": "1:355658314171:web:958625b62f8945b7be949e",
  "measurementId": "G-6YMQ4J7XLC"
}
#Initializing Firebase with Configs
firebase = pyrebase.initialize_app(config)
#Getting reference to Firebase Auth
fb_auth = firebase.auth()
fb_db = firebase.database()

def load_stuff(filename):
    saved_stuff = open(filename, "rb")
    stuff = pickle.load(saved_stuff)
    saved_stuff.close()
    return stuff


class FaceIdentify(object):
    """
    Singleton class for real time face identification
    """
    CASE_PATH = "/home/dj/WORK (Be Project)/sih2020/pretrained_models/haarcascade_frontalface_alt.xml"

    def __new__(cls, precompute_features_file=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FaceIdentify, cls).__new__(cls)
        return cls.instance

    def __init__(self, precompute_features_file=None):
        self.face_size = 224
        self.precompute_features_map = load_stuff(precompute_features_file)
        print("Loading VGG Face model...")
        self.model = VGGFace(model='resnet50',
                             include_top=False,
                             input_shape=(224, 224, 3),
                             pooling='avg')  # pooling: None, avg or max
        print("Loading VGG Face model done")

    @classmethod
    def draw_label(cls, image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale=1, thickness=2):
        size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        x, y = point
        cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
        cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness)

    def crop_face(self, imgarray, section, margin=20, size=224):
        """
        :param imgarray: full image
        :param section: face detected area (x, y, w, h)
        :param margin: add some margin to the face detected area to include a full head
        :param size: the result image resolution with be (size x size)
        :return: resized image in numpy array with shape (size x size x 3)
        """
        img_h, img_w, _ = imgarray.shape
        if section is None:
            section = [0, 0, img_w, img_h]
        (x, y, w, h) = section
        margin = int(min(w, h) * margin / 100)
        x_a = x - margin
        y_a = y - margin
        x_b = x + w + margin
        y_b = y + h + margin
        if x_a < 0:
            x_b = min(x_b - x_a, img_w - 1)
            x_a = 0
        if y_a < 0:
            y_b = min(y_b - y_a, img_h - 1)
            y_a = 0
        if x_b > img_w:
            x_a = max(x_a - (x_b - img_w), 0)
            x_b = img_w
        if y_b > img_h:
            y_a = max(y_a - (y_b - img_h), 0)
            y_b = img_h
        cropped = imgarray[y_a: y_b, x_a: x_b]
        resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
        resized_img = np.array(resized_img)
        print(resized_img)
        return resized_img, (x_a, y_a, x_b - x_a, y_b - y_a)

    def identify_face(self, features, threshold=100):
        distances = []
        for person in self.precompute_features_map:
            person_features = person.get("features")
            distance = spatial.distance.euclidean(person_features, features)
            distances.append(distance)
        min_distance_value = min(distances)
        min_distance_index = distances.index(min_distance_value)
        if min_distance_value < threshold:
            return self.precompute_features_map[min_distance_index].get("name")
        else:
            return "?"

    def detect_face(self,src):
        avg_att=[]
        face_cascade = cv2.CascadeClassifier(self.CASE_PATH)
        features_faces=0

        # 0 means the default video capture device in OS
        video_capture = cv2.VideoCapture(src)
        # video_capture = WebcamVideoStream(src=src).start()
        #frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
        video_capture.set(cv2.CAP_PROP_POS_MSEC,30*1000)
        frame_rate=20
        frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # at= AttenThread(frame_rate, frame_width, frame_height).start()
        mix5.initialize_frame(frame_rate, frame_width, frame_height)
        # infinite loop, break by key ESC
        while video_capture.isOpened():
            # if not video_capture.isOpened():
            #     time.sleep(5)
            # Capture frame-by-frame
            cv2.waitKey(70)
            #video_capture.set(cv2.CAP_PROP_POS_MSEC, 30*1000)
            grab,frame = video_capture.read()
           # frame=cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
            if grab == True:

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.2,
                    minNeighbors=10,
                    minSize=(64, 64)
                )



                # placeholder for cropped faces
                predicted_names= None
                face_imgs = np.empty((len(faces), self.face_size, self.face_size, 3))
                for i, face in enumerate(faces):
                    #cv2.imshow('frame',frame)
                    face_img, cropped = self.crop_face(frame, face, margin=10, size=self.face_size)
                    (x, y, w, h) = cropped
                    att = mix5.at(face_img)
                    # at.give_frame(face_img)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 200, 0), 2)
                    face_imgs[i, :, :, :] = face_img
                    #print(face_imgs)
                if len(face_imgs) > 0 and ((predicted_names is None) or "?" in predicted_names ): #less use of model
                    # generate features for each face
                   # with graph.as_default():
                   pass
                    #cv2.imshow('frame',face_imgs)
                     #   features_faces = self.model.predict(face_imgs)
                    #predicted_names = [self.identify_face(features_face) for features_face in features_faces]
            
                # draw results
                # for i, face in enumerate(faces):
                #     label = "{}".format(predicted_names[i])
                #     self.draw_label(frame, (face[0], face[1]), label)
                #     avg_att.append([att,label])

                #cv2.imshow('Keras Faces', frame)
                # if cv2.waitKey(5) == 27:  # ESC key press
                #     break
            else:
                break
        # When everything is done, release the capture
        #video_capture.release()
        # video_capture.stop()
        cv2.destroyAllWindows()
        # fb_db.child("avg-attentiveness").child(avg_att[::-1][0][1]).update({"dt": avg_att[::-1][0][0]['dt']})
        # fb_db.child("avg-attentiveness").child(avg_att[::-1][0][1]).update({"attentiveness": avg_att[::-1][0][0]['attentiveness']})




# def main():
#     face = FaceIdentify(precompute_features_file="./data/precompute_features.pickle")
#     face.detect_face()

# if __name__ == "__main__":
#     main()