import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from face_identify import FaceIdentify
#from AudioProcess import Audio_Analysis

import time
app = Flask(__name__)
api = Api(app)
CORS(app, resource={r"/": {"origins": "*"}})
face=FaceIdentify(precompute_features_file="./data/precompute_features.pickle")
#audio = Audio_Analysis()
class Upload(Resource):
    def post(self):
        print("File ali", request)
        if request.method == 'POST':
            file = request.files['file']
            if file.filename == '':
                return "Not Found", 404
            

            if file:
                print("File ali",file)
                filename = secure_filename(file.filename)
                file.save(filename)
                #os.system("ffmpeg -i v0.mp4 -c:a copy -s hd720 output3.mkv")
                #train(filename)
                #predict(moni=10)
                #audio.extract_audio("output3.mkv")
                time.sleep(2)
                face.detect_face(filename)

                return "OK", 200

api.add_resource(Upload, '/upload')
if __name__ == '__main__':
    app.run(port=5002)
