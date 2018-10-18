"""
Copyright 2015-2018 Jacob M. Graving <jgraving@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# import the necessary packages
from threading import Thread
import sys
import cv2
import time

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
	from queue import Queue

# otherwise, import the Queue class for Python 2.7
else:
	from Queue import Queue

class VideoReader:
    def __init__(self, path, queue_size=100):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.total_frames = self.stream.get(cv2.CAP_PROP_FRAME_COUNT)
        self.stopped = False
        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize=queue_size)

    def start(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        time.sleep(1)
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()
                
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                
                # add the frame to the queue
                self.Q.put(frame)

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def read_batch(self, n_frames, asarray=False):
        frames = []
        for idx in range(n_frames):
            frames.append(self.read())
        return frames


    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        
    def close(self):
        self.stop()