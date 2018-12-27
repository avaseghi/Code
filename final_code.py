import sys
sys.path.append('./axidraw/')
sys.path.append('./axidraw/pyaxidraw/')
sys.path.append('./axidraw/pyaxidraw/lib/')
import serial
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2
import numpy as np
from collections import OrderedDict
import svgwrite
import os
from pyaxidraw import axidraw   # Import the module
import OSC
c = OSC.OSCClient()

c.connect(('127.0.0.1', 5005))   # connect to SuperCollider

path = "./"

ser = serial.Serial('/dev/cu.wchusbserialfa130', 115200)

shapePredictor = "shape_predictor_68_face_landmarks.dat"

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shapePredictor)

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] camera sensor warming up...")
vs = VideoStream(0).start()
# time.sleep(2.0)

# face dimensions
face_detected = 0
face_x=0
face_y=0
face_w=0
face_h=0

target_origin_x = 0
target_origin_y = 80
target_width = 600
target_height = 750

FACIAL_LANDMARKS_68_IDXS = OrderedDict([
        ("mouth", (48, 68)),
        ("inner_mouth", (60, 68)),
        ("right_eyebrow", (17, 22)),
        ("left_eyebrow", (22, 27)),
        ("right_eye", (36, 42)),
        ("left_eye", (42, 48)),
        ("nose", (27, 36)),
        ("jaw", (0, 17))
])

FACIAL_LANDMARKS_IDXS = FACIAL_LANDMARKS_68_IDXS

def change_coordinate_space(pt, feature_w, feature_h, feature_x, feature_y):
    if float(feature_w)/float(feature_h) > float(target_width)/float(target_height):
        # print("too wide")
        wn = np.int64(feature_w)
        hn = np.int64(wn*target_height/target_width)
    else:
        # print("too high")
        hn = np.int64(feature_h)
        wn = np.int64(hn*target_width/target_height)

    x, y = pt

# now we have width new nad height new
    x_ = x - feature_x
    y_ = y - feature_y

    xn = x_ * target_width/wn + target_origin_x
    yn = y_ * target_height/hn + target_origin_y

    if xn > target_origin_x + target_width or yn > target_origin_y + target_height:
        print("!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!!!!!")
        print("target dimensions: ", target_origin_x, target_origin_y, target_width, target_height)
        print("feature dimensions: ", feature_x, feature_y, feature_w, feature_h)
        print("new width, height: ", wn, hn)
        sys.exit()

    if wn < feature_w or hn < feature_h:
        print("!!!!!!!!!!!!!!!!!!!ERROR2!!!!!!!!!!!!!!!!!!!!")
        print("target dimensions: ", target_origin_x, target_origin_y, target_width, target_height)
        print("feature dimensions: ", feature_x, feature_y, feature_w, feature_h)
        print("new width, height: ", wn, hn)
        sys.exit()

    return(tuple([np.int64(xn), np.int64(yn)]))

def draw_portrait(shape, face_w, face_h, face_x, face_y):
    print("Face dimensions: ", face_x, face_y, face_w, face_h)
    # create SVG file
    dwg = svgwrite.Drawing(filename='portrait.svg', size=(tuple(["650px", "792px"])), debug=True)
    # loop over the facial landmark regions individually
    max_x=0
    max_y=0
    min_x=9999
    min_y=9999

    for (i, name) in enumerate(FACIAL_LANDMARKS_IDXS.keys()):
        (j, k) = FACIAL_LANDMARKS_IDXS[name]
        pts = shape[j:k]

        # print(pts)

        for l in range(0, len(pts)):
            x,y=pts[l]
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y

    feature_x = min_x
    feature_y = min_y
    feature_w = max_x - min_x
    feature_h = max_y - min_y

    print("Modified Face dimensions: ", feature_x, feature_y, feature_w, feature_h)

    for (i, name) in enumerate(FACIAL_LANDMARKS_IDXS.keys()):
        # grab the (x, y)-coordinates associated with the
        # face landmark
        (j, k) = FACIAL_LANDMARKS_IDXS[name]
        pts = shape[j:k]

        # check if are supposed to draw the jawline
        if name == "jaw":
            # print("#######################JAW#########################")
            jaw_line = dwg.add(dwg.g(id='jaw_line', stroke='black'))
            # since the jawline is a non-enclosed facial region,
            # just draw lines between the (x, y)-coordinates
            # print(type(pts[0][0]))
            for l in range(1, len(pts)):
                ptA = tuple(pts[l - 1])
                ptA = change_coordinate_space(ptA, feature_w, feature_h, feature_x, feature_y)
                ptB = tuple(pts[l])
                ptB = change_coordinate_space(ptB, feature_w, feature_h, feature_x, feature_y)
                jaw_line.add(dwg.line(start = ptA, end = ptB))

        # otherwise, compute the convex hull of the facial
        # landmark coordinates points and display it
        else:
            features = dwg.add(dwg.g(id='features', stroke='black'))
            hull = cv2.convexHull(pts)
            points_array = []
            for pt in hull:
                # print(pt[0])
                points_array.append(tuple(pt[0]))

            for l in range(1, len(points_array)):
                ptA = tuple([np.int64(points_array[l - 1][0]), np.int64(points_array[l - 1][1])])
                ptA = change_coordinate_space(ptA, feature_w, feature_h, feature_x, feature_y)
                ptB = tuple([np.int64(points_array[l][0]), np.int64(points_array[l][1])])
                ptB = change_coordinate_space(ptB, feature_w, feature_h, feature_x, feature_y)
                # print("Type of point: ", type(ptB[0]))
                print(ptA, ptB)
                features.add(dwg.line(start = ptA, end = ptB))

            end_pt = tuple([np.int64(points_array[0][0]), np.int64(points_array[0][1])])
            end_pt = change_coordinate_space(end_pt, feature_w, feature_h, feature_x, feature_y)
            features.add(dwg.line(start = ptB, end = end_pt))

    dwg.save()

#check for negative values
def check_value_sanity(x, y, w, h, width, height):
    if(x > 0 and y > 0 and w > 0 and h > 0 and x + w < width and y + h < height):
        return 1
    else:
        return 0

def was_button_pressed():
    print("checking button")
    if  ser.in_waiting:
        input = str(ser.readline())
        print(input)
        if input.find("button pressed") != -1:
            return 1
        else:
            return 0
    else:
        return 0

def send_lights_off():
    print("Switch off light.")
    ser.write(b'off\n')

def send_restart():
    print("Restart.")
    ser.write(b'start\n')

def drawSVG():
    ad = axidraw.AxiDraw()          # Create class instance
    ad.plot_setup("portrait.svg")        # Load file & configure plot context
    # Plotting options can be set, here after plot_setup().
    ad.options.report_time = True
    ad.options.accel = 50
    ad.plot_run()                   # Plot the file
    print('Pencils down!')
    c.connect(('127.0.0.1', 5005))
    oscmsg = OSC.OSCMessage()
    oscmsg.setAddress("/test/")
    oscmsg.append(1)
    c.send(oscmsg)

def homeY():
    ad = axidraw.AxiDraw()          # Create class instance
    ad.plot_setup("./axidraw/homing_test.svg")
    ad.serial_connect()

    ioString = ad.readIO()
    yHomeStatus = int(ioString.split(',')[2]) & 0b00000100  # Y

    while yHomeStatus == 0:
        ad.moveYBack()

        ioString = ad.readIO()
        yHomeStatus = int(ioString.split(',')[2]) & 0b00000100  # Y
        print(yHomeStatus)

    ad.disconnect()

def homeX():
    ad = axidraw.AxiDraw()          # Create class instance
    ad.plot_setup("./axidraw/homing_test.svg")
    ad.serial_connect()

    ioString = ad.readIO()
    xHomeStatus = int(ioString.split(',')[2]) & 0b00001000  # X

    while xHomeStatus == 0:
        ad.moveXBack()

        ioString = ad.readIO()
        xHomeStatus = int(ioString.split(',')[2]) & 0b00001000  # X

    ad.disconnect()

print("Start homing Y")
homeY()
print("Start homing X")
homeX()
send_restart();

lastUpdateTime = int(round(time.time() * 1000));
needToUpdate = 1

while(True):
    print(int(round(time.time() * 1000)) - lastUpdateTime)
    if (int(round(time.time() * 1000)) - lastUpdateTime) > 70000 and needToUpdate == 1:
        print("sending header update")
        c.connect(('127.0.0.1', 5005))
        oscmsg = OSC.OSCMessage()
        oscmsg.setAddress("/test/")
        oscmsg.append(8)
        c.send(oscmsg)
        needToUpdate = 0
    if was_button_pressed() == 1:
        print("Button pressed")
        #get image
        face_detected = 0
        while face_detected == 0:
            print("Searching for face")
            # grab the frame from the threaded video stream, resize it to
            # have a maximum width of 400 pixels, and convert it to
            # grayscale
            frame = vs.read()
            # rotate frame
            frame = imutils.rotate_bound(frame, 90)
            original_frame = frame
            # cv2.imshow("Webcam", frame)
            frame = imutils.resize(frame, width=400)
            height, width = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect faces in the grayscale frame
            rects = detector(gray, 0)

            # print("rects: ", rects)

            # face dimensions
            face_detected = 0
            face_x=0
            face_y=0
            face_w=0
            face_h=0

            if len(rects):
            # loop over the face detections
                for rect in rects:
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a np
                # array
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)

                # convert dlib's rectangle to a OpenCV-style bounding box
                # [i.e., (x, y, w, h)], then draw the face bounding box
                    (x, y, w, h) = face_utils.rect_to_bb(rect)
                    if(check_value_sanity(x, y, w, h, width, height) == 1):
                        if(h > face_h):
                            face_x = x
                            face_y = y
                            face_w = w
                            face_h = h
                            face_detected = 1

                # end of face detection
                    if(face_detected == 1):
                        print("##############################################################")
                        print("Face detected at: ", face_x, face_y, face_w, face_h)

                        img_name = "./images/opencv_frame_"+str(int(round(time.time() * 1000)))+".jpg"
                        print("Saving file to: ", img_name)
                        cv2.imwrite(img_name, original_frame)
                        draw_portrait(shape, face_w, face_h, face_x, face_y)
                        needToUpdate = 1
                        lastUpdateTime = int(round(time.time() * 1000));
        # face is saved as ./portrait.svg

        send_lights_off();
        #draw image
        # tell canvas to clear
        c.connect(('127.0.0.1', 5005))
        oscmsg = OSC.OSCMessage()
        oscmsg.setAddress("/test/")
        oscmsg.append(9)
        c.send(oscmsg)
        print("Start homing")
        # home axidraw
        homeY()
        homeX()
        print("done homing")
        # tell axidraw to draw
        ad = axidraw.AxiDraw()          # Create class instance
        ad.plot_setup("portrait.svg")        # Load file & configure plot context
        # Plotting options can be set, here after plot_setup().
        ad.options.report_time = True
        ad.plot_run()                   # Plot the file
        print('Pencils down!')
        c.connect(('127.0.0.1', 5005))
        oscmsg = OSC.OSCMessage()
        oscmsg.setAddress("/test/")
        oscmsg.append(1)
        c.send(oscmsg)
        # home axidraw
        homeY()
        homeX()
        #done drawing
        send_restart()
