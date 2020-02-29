from threading import Thread
import cv2
import mix5 as mx
class AttenThread:
    def __init__(self, fr,fw,fh):
		# initialize the video camera stream and read the first frame
		# from the stream
        self.mx=mx
        self.mx.initialize_frame(fr,fw,fh)
        self.stopped=False
        self.frame=None
        
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            if self.frame is None:
                pass
            else:
                self.mx.at(self.frame)
    def give_frame(self,frame):
        self.frame=frame
    def stop(self):
        self.stopped=True
    # def isOpened(self):
    #     return self.stream.isOpened()
    # def get(self, arg):
    #     return self.stream.get(arg)