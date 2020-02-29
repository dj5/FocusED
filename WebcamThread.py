from threading import Thread
import cv2
class WebcamVideoStream:
    def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
		# initialize the variable used to indicate if the thread should
		# be stopped
        self.stopped = False
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return 
            (self.grabbed,self.frame)=self.stream.read()
    def read(self):
        return self.frame
    def stop(self):
        self.stopped=True
    def isOpened(self):
        return self.stream.isOpened()
    def get(self, arg):
        return self.stream.get(arg)
    def set(self,con,sec):
        self.stream.set(con,sec)
    def grab(self):
        return self.grabbed