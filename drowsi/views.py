from django.shortcuts import render
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import math
from cv2 import cv2
import numpy as np
import winsound
from scipy.spatial import distance as dist
import math
import numpy as np
from cv2 import cv2
import requests


def button(request):
    return render(request,'home.html')

def input(request):
    return render(request, 'test.html')

def contact(request):
    return render(request, 'contact.html')

def last(request):
    return render(request, 'test.html')
def output(request):
        #!/usr/bin/env python

        model_points = np.array([
        (0.0, 0.0, 0.0),             # Nose tip 34
        (0.0, -330.0, -65.0),        # Chin 9
        (-225.0, 170.0, -135.0),     # Left eye left corner 37
        (225.0, 170.0, -135.0),      # Right eye right corne 46
        (-150.0, -150.0, -125.0),    # Left Mouth corner 49
        (150.0, -150.0, -125.0)      # Right mouth corner 55
        ])

        # Checks if a matrix is a valid rotation matrix.
        def isRotationMatrix(R):
            Rt = np.transpose(R)
            shouldBeIdentity = np.dot(Rt, R)
            I = np.identity(3, dtype=R.dtype)
            n = np.linalg.norm(I - shouldBeIdentity)
            return n < 1e-6


        # Calculates rotation matrix to euler angles
        # The result is the same as MATLAB except the order
        # of the euler angles ( x and z are swapped ).
        def rotationMatrixToEulerAngles(R):
            assert(isRotationMatrix(R))
            sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
            singular = sy < 1e-6
            if not singular:
                x = math.atan2(R[2, 1], R[2, 2])
                y = math.atan2(-R[2, 0], sy)
                z = math.atan2(R[1, 0], R[0, 0])
            else:
                x = math.atan2(-R[1, 2], R[1, 1])
                y = math.atan2(-R[2, 0], sy)
                z = 0
            return np.array([x, y, z])


        def getHeadTiltAndCoords(size, image_points, frame_height):
            focal_length = size[1]
            center = (size[1]/2, size[0]/2)
            camera_matrix = np.array([[focal_length, 0, center[0]], [
                0, focal_length, center[1]], [0, 0, 1]], dtype="double")

            # print "Camera Matrix :\n {0}".format(camera_matrix)

            dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
            (_, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points,
                                                                        camera_matrix, dist_coeffs,
                                                                        flags = cv2.SOLVEPNP_ITERATIVE)  # flags=cv2.CV_ITERATIVE)

            # print "Rotation Vector:\n {0}".format(rotation_vector)
            # print "Translation Vector:\n {0}".format(translation_vector)
            # Project a 3D point (0, 0 , 1000.0) onto the image plane
            # We use this to draw a line sticking out of the nose_end_point2D
            (nose_end_point2D, _) = cv2.projectPoints(np.array(
                [(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)

            #get rotation matrix from the rotation vector
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

            #calculate head tilt angle in degrees
            head_tilt_degree = abs(
                [-180] - np.rad2deg([rotationMatrixToEulerAngles(rotation_matrix)[0]]))

            #calculate starting and ending points for the two lines for illustration
            starting_point = (int(image_points[0][0]), int(image_points[0][1]))
            ending_point = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

            ending_point_alternate = (ending_point[0], frame_height // 2)

            return head_tilt_degree, starting_point, ending_point, ending_point_alternate



        def eye_aspect_ratio(eye):
            # compute the euclidean distances between the two sets of
            # vertical eye landmarks (x, y)-coordinates
            A = dist.euclidean(eye[1], eye[5])
            B = dist.euclidean(eye[2], eye[4])
            # compute the euclidean distance between the horizontal
            # eye landmark (x, y)-coordinates
            C = dist.euclidean(eye[0], eye[3])
            # compute the eye aspect ratio
            ear = (A + B) / (2.0 * C)
            # return the eye aspect ratio
            return ear
        def mouth_aspect_ratio(mouth):
            # compute the euclidean distances between the two sets of
            # vertical mouth landmarks (x, y)-coordinates
            A = dist.euclidean(mouth[2], mouth[10])  # 51, 59
            B = dist.euclidean(mouth[4], mouth[8])  # 53, 57

            # compute the euclidean distance between the horizontal
            # mouth landmark (x, y)-coordinates
            C = dist.euclidean(mouth[0], mouth[6])  # 49, 55

            # compute the mouth aspect ratio
            mar = (A + B) / (2.0 * C)

            # return the mouth aspect ratio
            return mar

        # initialize dlib's face detector (HOG-based) and then create the
        # facial landmark predictor
        print("[INFO] loading facial landmark predictor...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(
            './dlib_shape_predictor/shape_predictor_68_face_landmarks.dat')

        # initialize the video stream and sleep for a bit, allowing the
        # camera sensor to warm up
        print("[INFO] initializing camera...")

        vs = VideoStream(src=1).start()
        # vs = VideoStream(usePiCamera=True).start() # Raspberry Pi
        time.sleep(2.0)

        # 400x225 to 1024x576
        frame_width = 1024
        frame_height = 576

        # loop over the frames from the video stream
        # 2D image points. If you change the image, you need to change vector
        image_points = np.array([
            (359, 391),     # Nose tip 34
            (399, 561),     # Chin 9
            (337, 297),     # Left eye left corner 37
            (513, 301),     # Right eye right corne 46
            (345, 465),     # Left Mouth corner 49
            (453, 469)      # Right mouth corner 55
        ], dtype="double")

        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        EYE_AR_THRESH = 0.23
        MOUTH_AR_THRESH = 0.79
        EYE_AR_CONSEC_FRAMES = 3
        COUNTER = 0

        # grab the indexes of the facial landmarks for the mouth
        (mStart, mEnd) = (49, 68)
        cap=cv2.VideoCapture(0)

        while True:
            # grab the frame from the threaded video stream, resize it to
            # have a maximum width of 400 pixels, and convert it to
            # grayscale
            ret, frame = cap.read()
            frame = imutils.resize(frame, width=700)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            size = gray.shape

            # detect faces in the grayscale frame
            rects = detector(gray, 0)

            # check to see if a face was detected, and if so, draw the total
            # number of faces on the frame


            # loop over the face detections
            for rect in rects:
                # compute the bounding box of the face and draw it on the
                # frame
                (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
                cv2.rectangle(frame, (bX, bY), (bX + bW, bY + bH), (0, 255, 0), 1)
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                # extract the left and right eye coordinates, then use the
                # coordinates to compute the eye aspect ratio for both eyes
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                # average the eye aspect ratio together for both eyes
                ear = (leftEAR + rightEAR) / 2.0

                # compute the convex hull for the left and right eye, then
                # visualize each of the eyes
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                # check to see if the eye aspect ratio is below the blink
                # threshold, and if so, increment the blink frame counter
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    # if the eyes were closed for a sufficient number of times
                    # then show the warning
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        winsound.Beep(440, 500)
                        cv2.putText(frame, "**************************ALERT!****************************", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "**************************ALERT!****************************", (10, 500),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # otherwise, the eye aspect ratio is not below the blink
                    # threshold, so reset the counter and alarm
                else:
                    COUNTER = 0

                mouth = shape[mStart:mEnd]

                mouthMAR = mouth_aspect_ratio(mouth)
                mar = mouthMAR
                # compute the convex hull for the mouth, then
                # visualize the mouth
                mouthHull = cv2.convexHull(mouth)

                cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)


                # Draw text if mouth is open
                if mar > MOUTH_AR_THRESH:
                    winsound.Beep(440, 500)
                    cv2.putText(frame, "**********ALERT!**********", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "**********ALERT!**********", (10, 500),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


                # loop over the (x, y)-coordinates for the facial landmarks
                # and draw each of them
                for (i, (x, y)) in enumerate(shape):
                    if i == 33:
                        # something to our key landmarks
                        # save to our new key point list
                        # i.e. keypoints = [(i,(x,y))]
                        image_points[0] = np.array([x, y], dtype='double')
                        # write on frame in Green
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 8:
                        # something to our key landmarks
                        # save to our new key point list
                        # i.e. keypoints = [(i,(x,y))]
                        image_points[1] = np.array([x, y], dtype='double')
                        # write on frame in Green
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 36:
                        # something to our key landmarks
                        # save to our new key point list
                        # i.e. keypoints = [(i,(x,y))]
                        image_points[2] = np.array([x, y], dtype='double')
                        # write on frame in Green
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 45:
                        # something to our key landmarks
                        # save to our new key point list
                        # i.e. keypoints = [(i,(x,y))]
                        image_points[3] = np.array([x, y], dtype='double')
                        # write on frame in Green
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 48:
                        # something to our key landmarks
                        # save to our new key point list
                        # i.e. keypoints = [(i,(x,y))]
                        image_points[4] = np.array([x, y], dtype='double')
                        # write on frame in Green
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 54:
                        # something to our key landmarks
                        # save to our new key point list
                        # i.e. keypoints = [(i,(x,y))]
                        image_points[5] = np.array([x, y], dtype='double')
                        # write on frame in Green
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    else:
                        # everything to all other landmarks
                        # write on frame in Red
                        cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                #Draw the determinant image points onto the person's face
                for p in image_points:
                    cv2.circle(frame, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

                (head_tilt_degree, start_point, end_point, 
                    end_point_alt) = getHeadTiltAndCoords(size, image_points, frame_height)

                cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
                cv2.line(frame, start_point, end_point_alt, (0, 0, 255), 2)

                if head_tilt_degree:
                    cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # extract the mouth coordinates, then use the
                # coordinates to compute the mouth aspect ratio
            # show the frameq
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # print(image_points)

        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()
        return render(request,'test.html')