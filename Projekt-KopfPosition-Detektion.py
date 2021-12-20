import cv2
import time
import math
import numpy as np
import PoseModule as pm
#############

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)
pTime = 0
detector = pm.poseDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()

VolRange = volume.GetVolumeRange()
MinVol1 = VolRange[0]
MaxVol1 = VolRange[1]
MinVol2 = VolRange[0]
MaxVol2 = VolRange[1]
vol1 = 0
vol2 = 0
vol1Bar = 400
vol2Bar = 400
vol1Per = 0
vol2Per = 0

while True:
    success, img = cap.read()
    img = detector.findPose(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[14], lmList[12], lmList[11])

        x1, y1= lmList[0][1], lmList[0][2] # point 1
        x2, y2 = lmList[12][1], lmList[12][2] #Point 2
        x3, y3 = lmList[11][1], lmList[11][2] # Point 3
        Ax, Ay = (x1 + x2) // 2, (y1 + y2) // 2 #Center 1 -Rechte seite
        Bx, Bz = (x1 + x3) // 2, (y1 + y3) // 2 #Center 2 -Linke Seite

        #Point
        cv2.circle(img, (x1,y1), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x3, y3), 5, (255, 0, 255), cv2.FILLED)
        #line of Point
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 1)
        cv2.line(img, (x1, y1), (x3, y3), (255, 0, 255), 1)

        #center of line
        cv2.circle(img, (Ax, Ay), 5, (255, 0, 255), cv2.FILLED) # Nach Rechte seite
        cv2.circle(img, (Bx, Bz), 5, (255, 0, 255), cv2.FILLED) # Nach Linke Seite

        length1 = math.hypot(x2 - x1, y2 - y1)
        length2 = math.hypot(x1 - x3, y3 + y1)
        #length = math.hypot(x2 - x1, y2 - y1, x3 - x1, y3 + y1)
        #print(length2)

        # Kopf range 50 - 650
        # Volume Range -60 - 0

        vol1 = np.interp(length1, [190, 300], [MinVol1, MaxVol1])
        print(int(length1), vol1)
        vol1Bar = np.interp(length1, [190, 240], [400, 150])
        vol1Per = np.interp(length1, [190, 240], [0, 100])

        vol2 = np.interp(length2, [770, 910], [MinVol2, MaxVol2])
        #print(int(length2), vol1)
        vol2Bar = np.interp(length2, [770, 810], [400, 150])
        vol2Per = np.interp(length2, [770, 810], [0, 100])
        volume.SetMasterVolumeLevel(vol1, None)
        volume.SetMasterVolumeLevel(vol2, None)


        if length1 > 240:
            cv2.circle(img, (Ax, Ay), 5, (0, 255, 0), cv2.FILLED)  # Linke Seite Grüne Leuchtet

        if length2 > 810:
            cv2.circle(img, (Bx, Bz), 5, (0, 255, 0), cv2.FILLED)  # Rechte seite Grüne Leuchtet

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(vol1Bar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(vol1Per)} %', (42, 420), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0), 3)

    cv2.rectangle(img, (135, 150), (170, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (135, int(vol2Bar)), (170, 400), (255, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(vol2Per)} %', (130, 420), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 0), 3)


        #cv2.circle(img, (lmList[0][1], lmList[0][2]), 10, (0, 0, 255), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)