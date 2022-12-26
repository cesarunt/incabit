import numpy as np
import imutils, os
import time
import cv2
from datetime import timedelta
# Librarys for Object Detect
from setting.config import cfg
import core_yolo.utils as utils
# Librarys for Distance Detect
from core_yolo.distance.detection import detect_people
from core_utils.detect_loitering import loitering_people, coords_PeopleInSquare
from shapely.geometry import Point, Polygon
import threading
import subprocess


global weightsPath, configPath, squaresize, net, ln

namesPath   = cfg.YOLO.V3_NAMES
configPath  = cfg.YOLO.V3_CFG
weightsPath = cfg.YOLO.V3_WEIGHTS
squaresize  = cfg.YOLO.SQUARESIZE

# load the COCO class labels our YOLO model was trained on
LABELS = open(namesPath).read().strip().split("\n")

# Calculate the time - start
##    start_time = time.time()
# Set data for YOLO object detector
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def play_alarm(file_name = ""):
    process = subprocess.Popen(["afplay", file_name], shell=False)
    time.sleep(6)
    process.kill()

def alert_after_timeout(path = ""):
    process = None
    thread = threading.Thread(target=play_alarm(path+"/alert_loiter_01.mp3"))
    thread.start()
    thread.join()

def generateImage_socialDistance(image, W, H, localConfidence=cfg.YOLO.CONFIDENCE):
    image_result = None
    # 2. Detecting objects 
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (squaresize, squaresize), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    # 3. Processing objects' layers
    boxes, centroids, confidences = utils.processLayers_oneObject(layerOutputs, W, H, localConfidence, objectIdx=LABELS.index("person"))
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, localConfidence, cfg.YOLO.THRESHOLD)

    thick = 1
    if W > 1200: thick = 2
    if W > 2500: thick = 3
    results = []

    # 4. Get boxes, and text over image result
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            r = (confidences[i], (x, y, x + w, y + h), centroids[i])
            results.append(r)
        
        list_input = [boxes, centroids, confidences]
        image_result  = utils.draw_boxes_socialDistance(image, results, list_input, thick)
    
    if image_result is not None:
        return image_result
    else:
        return None

def generateImage_analyticsDetectObjects(image, W, H, localConfidence=cfg.YOLO.CONFIDENCE, _object=None):
    image_result = None
    # 2. Detecting objects 
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (squaresize, squaresize), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    thick = 1
    if W > 1300: thick = 2
    if W > 2600: thick = 3
    
    # 3. Processing objects' layers
    if (_object==None):
        boxes, confidences, classIDs = utils.processLayers_allObject(layerOutputs, W, H, localConfidence)
    else:
        boxes, confidences, classIDs = utils.processLayers_searchObject(layerOutputs, W, H, localConfidence, LABELS.index(_object))

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, localConfidence, cfg.YOLO.THRESHOLD)
    # 4. Drawing boxes, and text over image result
    if len(idxs) > 0:
        list_input = [boxes, confidences, classIDs]
        image_result  = utils.draw_boxes_analyticsDetectObjects(image, idxs, list_input, thick)
    
    if image_result is not None:
        return image_result
    else:
        return None

def generateImage_analyticsCountPersons(image, W, H, localConfidence=cfg.YOLO.CONFIDENCE):
    image_result = None
    # 2. Detecting objects 
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (squaresize, squaresize), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    thick = 1
    if W > 1200: thick = 2
    if W > 2500: thick = 3
    results = []

    # 3. Processing objects' layers
    boxes, centroids, confidences = utils.processLayers_oneObject(layerOutputs, W, H, localConfidence, objectIdx=LABELS.index("person"))
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, localConfidence, cfg.YOLO.THRESHOLD)

    # 4. Get boxes, and text over image result
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            r = (confidences[i], (x, y, x + w, y + h), centroids[i])
            results.append(r)
        list_input = [boxes, centroids, confidences]
        image_result  = utils.draw_boxes_analyticsCountPersons(image, results, list_input, thick)

    if image_result is not None:
        return image_result
    else:
        return None

def generateImage_loiteringDetectObjects(image, W, H, localConfidence=cfg.YOLO.CONFIDENCE, path=None, loiter_dict=None, _object=None):
    # Set coordinates for geometric figure (6-sided polygon)
    coords_polylines, coords_polygon = coords_PeopleInSquare(W, H)
    loiter_polyarea = Polygon(coords_polygon)
    loiter_numperson = loiter_dict.get('loiter_numperson')
    loiter_band      = loiter_dict.get('loiter_band')
    loiter_timeI     = loiter_dict.get('loiter_timeI')
    loiter_timeE     = loiter_dict.get('loiter_timeE')
    text_alert       = loiter_dict.get('loiter_text_alert')
    i                = loiter_dict.get('loiter_i')
    j                = loiter_dict.get('loiter_j')

    # Draw the polygon area from your coords
    cv2.polylines(image, [coords_polylines], True, (255,255,255), thickness=2)

    # -------------------------------------------------------------------------
    image_result = None
    # 2. Detecting objects 
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (squaresize, squaresize), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    thick = 1
    if W > 1200: thick = 2
    if W > 2500: thick = 3
    results = []

    # 3. Processing objects' layers
    boxes, centroids, confidences = utils.processLayers_oneObject(layerOutputs, W, H, localConfidence, objectIdx=LABELS.index(_object))
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, localConfidence, cfg.YOLO.THRESHOLD)

    # 4. Get boxes, and text over image result
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            r = (confidences[i], (x, y, x + w, y + h), centroids[i])
            results.append(r)

    loiter_numperson = 0
    color_text = (255, 255, 255)

    # loop over the results
    for (k, (prob, bbox, centroid)) in enumerate(results):
        (startX, startY, endX, endY) = bbox
        (cX, cY) = centroid
        color_obj = (0, 255, 0)
        # Checks if a point is within a polygon
        point = Point(cX, cY)
        if (point.within(loiter_polyarea)==True):
            cv2.polylines(image, [coords_polylines], True, (0,0,255), thickness=2)
            loiter_numperson += 1
            color_obj = (0, 0, 255)
        # Draw objects in the image, include loitering area
        cv2.rectangle(image, (startX, startY), (endX, endY), color_obj, 1)
        cv2.circle(image, (cX, cY), 4, color_obj, 1)

    if loiter_numperson > 0 :
        if loiter_band==False:
            loiter_timeI = time.time()
        loiter_band = True
        color_text = (0, 0, 255)
    else:
        text_alert = ""
        loiter_band = False
        loiter_timeI = time.time()

    # Set x,y values for text
    x = 25
    y = 40
    # Show time elapsed of loitering
    loiter_timeE = time.time() - loiter_timeI
    text2 = "Tiempo de Merodeo: {:.2f}/15.0".format(loiter_timeE)
    cv2.putText(image, text2, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color_text, 2)

    if loiter_timeE > 17.0 :
        # Text Alert, to put on screen
        j = 1000
        # Call Alert with sound
        alert_after_timeout(path)
        loiter_band = False
        loiter_timeI = time.time()
        # Saving the image on ../files/alerts
        fil_image = path+"/mdb/loiter_alert_"+str(loiter_timeI)+".jpg"
        save_image = cv2.imwrite(fil_image, image)
        # Send message by WhatsApp
        web_image = "files/alerts/mdb/loiter_alert_"+str(loiter_timeI)+".jpg"
        os.system("php send_msg.php %s"%(web_image))
    
    j += 1
    if j>1000 and j < 1006:
        text_alert = "Alerta: INTRUSO DETECTADO"
        cv2.rectangle(image, (x, y*2-15), (x + 545, y*2 + 35), (225,225,225), -1)
        cv2.putText(image, text_alert, (x, y*2+21), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0,0,225), 2)
    else:
        j = 0
    
    image_result = image
    new_loiter_dict = { 'loiter_numperson' : loiter_numperson,
                        'loiter_band'      : loiter_band,
                        'loiter_timeI'     : loiter_timeI,
                        'loiter_timeE'     : loiter_timeE,
                        'loiter_text_alert': text_alert,
                        'loiter_i'         : i,
                        'loiter_j'         : j
                    }

    return new_loiter_dict, image_result 