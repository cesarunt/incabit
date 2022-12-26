# utils.py
# Main functions

import cv2
import random
import colorsys
import numpy as np
from setting.config import cfg
from scipy.spatial import distance as dist

# load the COCO class labels to get COLORS
labelsPath = cfg.YOLO.V3_NAMES
LABELS = open(labelsPath).read().strip().split("\n")
# initialize a list of colors to represent each possible class label
np.random.seed(0)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 4), dtype="uint8")

def draw_text(dst, target, text, fontScale, thick):
    x, y = target
    cv2.putText(dst, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 255, 255), thickness = thick, lineType=cv2.LINE_AA)
    cv2.putText(dst, text, (x+thick, y+thick), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0, 0, 255), thickness = thick, lineType=cv2.LINE_AA)


def processLayers_allObject(layerOutputs, W, H, localConfidence):
    # initialize our lists of detected bounding boxes, confidences, and class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > localConfidence:
                # scale the bounding box coordinates back relative to the size of image
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our list of bounding box coordinates, confidences, and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
    
    return boxes, confidences, classIDs

def processLayers_searchObject(layerOutputs, W, H, localConfidence, objectIdx=0):
    # initialize our lists of detected bounding boxes, confidences, and class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if classID == objectIdx and confidence > localConfidence:
                # scale the bounding box coordinates back relative to the size of image
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our list of bounding box coordinates, confidences, and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
    
    return boxes, confidences, classIDs

def processLayers_oneObject(layerOutputs, W, H, localConfidence, objectIdx=0):
    # initialize our lists of detected bounding boxes, confidences, and class IDs, respectively
    boxes = []
    centroids = []
    confidences = []
    
    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability)
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if classID == objectIdx and confidence > localConfidence:
                # scale the bounding box coordinates back relative to the size of the image
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our list of bounding box coordinates, confidences, and class IDs
                boxes.append([x, y, int(width), int(height)])
                centroids.append((centerX, centerY))
                confidences.append(float(confidence))
    
    return boxes, centroids, confidences


def draw_boxes_analyticsDetectObjects(image, idxs, list_input, thick = 1):
    # local variables
    fontThickness = 1
    fontScale = 0.3 * thick
    fontFace  = cv2.FONT_HERSHEY_SIMPLEX
    #obj_detected = []

    boxes, confidences, classIDs = list_input
    # loop over the indexes we are keeping
    for i in idxs.flatten():
        # extract the bounding box coordinates
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        
        color = [int(c) for c in COLORS[classIDs[i]]]
        #color = colors[classIDs[i]]
        text = "{}: {:.2f}".format(LABELS[classIDs[i]], confidences[i])
        #obj_detected.append(LABELS[classIDs[i]])

        # Rectangle por text
        t_size = cv2.getTextSize(text, fontFace, fontScale, fontThickness)[0]
        cv2.rectangle(image, (x, y), (x + t_size[0], y - t_size[1]-5), color, -1)
        # Text
        cv2.putText(image, text, (x, y - 4), fontFace, fontScale, (0,0,0), fontThickness, lineType=cv2.LINE_AA)
        # Rectangle por object
        cv2.rectangle(image, (x, y), (x + w, y + h), color, thick, lineType=cv2.LINE_AA)
    
    return image#, obj_detected

def draw_boxes_socialDistance(image, results, list_input, thick = 1):
    # initialize the set of indexes that violate the minimum social distance
    violate = set()

    # local variables
    fontThickness = thick
    fontScale = 0.5 * thick
    fontFace  = cv2.FONT_HERSHEY_SIMPLEX
    ##obj_detected = []
    boxes, centroids, confidences = list_input

    # ensure there are *at least* two people detections (required in order to compute our pairwise distance maps)
    if len(results) >= 2:
        # extract all centroids from the results and compute the
        # Euclidean distances between all pairs of the centroids
        centroids = np.array([r[2] for r in results])
        D = dist.cdist(centroids, centroids, metric="euclidean")

        # loop over the upper triangular of the distance matrix
        for i in range(0, D.shape[0]):
            for j in range(i + 1, D.shape[1]):
                # check to see if the distance between any two centroid pairs
                # is less than the configured number of pixels
                if D[i, j] < cfg.YOLO.MIN_DISTANCE * thick:
                    # update our violation set with the indexes of the centroid pairs
                    violate.add(i)
                    violate.add(j)

    band = 0	# Si es un número seguido
    # loop over the results
    for (i, (prob, bbox, centroid)) in enumerate(results):
        # extract the bounding box and centroid coordinates, then
        # initialize the color of the annotation
        (startX, startY, endX, endY) = bbox
        (cX, cY) = centroid
        color = (0, 255, 0)

        # if the index pair exists within the violation set, then update the color
        if i in violate:
            color = (0, 0, 255)
            band += 1
        else:
            band = 0

        # draw (1) a bounding box around the person and (2) the centroid coordinates of the person
        cv2.rectangle(image, (startX, startY), (endX, endY), color, thick)
        cv2.circle(image, (cX, cY), 4, color, thick)
    
    # draw the total number of social distancing violations on the output frame
    text = "Total Violaciones: {}".format(int(len(violate)/2))
    t_size = cv2.getTextSize(text, fontFace, fontScale, thick)[0]
    # cv2.rectangle(image, (0, image.shape[0] - (t_size[1]*2) - 10), (t_size[0] + 20, image.shape[0] - 10), (250,250,250), -1)
    # cv2.putText(image, text, (10, image.shape[0] - 20), fontFace, fontScale, (0, 0, 255), thick)
    draw_text(image, (30, 50), text, fontScale, fontThickness)
    
    return image#, obj_detected

def draw_boxes_analyticsCountPersons(image, results, list_input, thick = 1):
    # initialize the set of indexes that violate the minimum social distance

    # local variables
    fontThickness = thick
    fontScale = 0.6 * thick
    fontFace  = cv2.FONT_HERSHEY_SIMPLEX
    ##obj_detected = []
    boxes, centroids, confidences = list_input

    # ensure there are *at least* two people detections (required in order to compute our pairwise distance maps)
    if len(results) >= 1:
        centroids = np.array([r[2] for r in results])

    # loop over the results
    for (i, (prob, bbox, centroid)) in enumerate(results):
        (startX, startY, endX, endY) = bbox
        (cX, cY) = centroid
        # green color
        color = (0, 255, 0)

        # draw (1) a bounding box around the person and (2) the centroid coordinates of the person
        cv2.rectangle(image, (startX, startY), (endX, endY), color, thick)
        #cv2.circle(image, (cX, cY), 5, color, -1)
    
    # draw the total number of social distancing violations on the output frame
    text = "Total Personas: {}".format(int(len(results)))
    t_size = cv2.getTextSize(text, fontFace, fontScale, thick)[0]
    #cv2.rectangle(image, (0, image.shape[0] - (t_size[1]*2) - 10), (t_size[0] + 20, image.shape[0] - 10), (250,250,250), -1)
    ##cv2.putText(image, text, (10, image.shape[0] - 20), fontFace, fontScale, (0, 0, 255), thick)
    draw_text(image, (30, 50), text, fontScale, fontThickness)
    
    return image #, obj_detected