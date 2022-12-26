# import the necessary packages
# from .config import NMS_THRESH
# from .config import MIN_CONF
import numpy as np
import cv2

# initialize minimum probability to filter weak detections along with
# the threshold when applying non-maxima suppression
MIN_CONF = 0.3
NMS_THRESH = 0.3

# boolean indicating if NVIDIA CUDA GPU should be used
USE_GPU = False

# define the minimum safe distance (in pixels) that two people can be from each other
MIN_DISTANCE = 60

# Frames to be fast or slow
NFRAMES=10

def loitering_people(frame, net, ln, personIdx=0):
	# grab the dimensions of the frame and  initialize the list of
	# results
	(H, W) = frame.shape[:2]
	results = []

	# construct a blob from the input frame and then perform a forward
	# pass of the YOLO object detector, giving us our bounding boxes
	# and associated probabilities
	blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
	#blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (104.0, 177.0, 123.0), True, crop=False)
	
	net.setInput(blob)
	layerOutputs = net.forward(ln)

	# initialize our lists of detected bounding boxes, centroids, and
	# confidences, respectively
	boxes = []
	centroids = []
	confidences = []

	# loop over each of the layer outputs
	for output in layerOutputs:
		# loop over each of the detections
		for detection in output:
			# extract the class ID and confidence (i.e., probability)
			# of the current object detection
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]

			# filter detections by (1) ensuring that the object
			# detected was a person and (2) that the minimum
			# confidence is met
			if classID == personIdx and confidence > MIN_CONF:
				# scale the bounding box coordinates back relative to the size
				# of the image, keeping in mind that YOLO actually returns 
				# the center (x, y)-coordinates of the bounding box followed by the boxes' width and
				# height
				box = detection[0:4] * np.array([W, H, W, H])
				(centerX, centerY, width, height) = box.astype("int")

				# use the center (x, y)-coordinates to derive the top
				# and and left corner of the bounding box
				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))

				# update our list of bounding box coordinates,
				# centroids, and confidences
				boxes.append([x, y, int(width), int(height)])
				centroids.append((centerX, centerY))
				confidences.append(float(confidence))

	# apply non-maxima suppression to suppress weak, overlapping
	# bounding boxes
	idxs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONF, NMS_THRESH)

	# ensure at least one detection exists
	if len(idxs) > 0:
		# loop over the indexes we are keeping
		for i in idxs.flatten():
			# extract the bounding box coordinates
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])

			# update our results list to consist of the person
			# prediction probability, bounding box coordinates,
			# and the centroid
			r = (confidences[i], (x, y, x + w, y + h), centroids[i])
			results.append(r)

	# return the list of results
	return results

# 0
# Set coords for Stole-house (Persons)
def coords_PeopleInSquare(frame_width, frame_height):
	coords_polylines = np.array([
                    [1, int(frame_height/2)+200], 
                    [120,int(frame_height/2)+105],
                    [int(frame_width)-200,int(frame_height/2)-125],
                    [int(frame_width-1),  int(frame_height/2)+120],
                    [int(frame_width-260),  int(frame_height-1)],
                    [1, int(frame_height)-1],
                    ])
	coords_polygon = [
	                (1, int(frame_height/2)+200), 
                    (120,int(frame_height/2)+105),
                    (int(frame_width)-200,int(frame_height/2)-125),
                    (int(frame_width-1),  int(frame_height/2)+120),
                    (int(frame_width-260),  int(frame_height-1)),
                    (1, int(frame_height)-1),
                	]
	return coords_polylines, coords_polygon

# 1
# Set coords for Stole-house (Persons)
def coords_PeopleInHouse(frame_width, frame_height):
	coords_polylines = np.array([
                    [int(frame_width/2)-200,int(frame_height/2)-210], 
                    [frame_width-110,int(frame_height/2)+50],
                    [frame_width-160,int(frame_height/2)+280],
                    [frame_width-350,frame_height], 
                    [int(frame_width/2)-300,int(frame_height/2)-20],
                    [int(frame_width/2)-200,int(frame_height/2)-50],
                    ])
	coords_polygon = [
	                (int(frame_width/2)-200,int(frame_height/2)-210), 
	                (frame_width-110,int(frame_height/2)+50),
	                (frame_width-160,int(frame_height/2)+280),
	                (frame_width-350,frame_height),
	                (int(frame_width/2)-300,int(frame_height/2)-20),
	                (int(frame_width/2)-200,int(frame_height/2)-50),
                	]
	return coords_polylines, coords_polygon

# frame_width = 1280
# frame_height = int(frame_height * (800/frame_width))
# area_pts = np.array([
#                     [int(frame_width/2)-100,int(frame_height/2)-310], 
#                     [frame_width-10,int(frame_height/2)-50],
#                     [frame_width-60,int(frame_height/2)+180],
#                     [frame_width-250,frame_height-100], 
#                     [int(frame_width/2)-200,int(frame_height/2)-120],
#                     [int(frame_width/2)-100,int(frame_height/2)-150],
#                     ])
# loiter_coords = [
#                 (int(frame_width/2)-200,int(frame_height/2)-210), 
#                 (frame_width-110,int(frame_height/2)+50),
#                 (frame_width-160,int(frame_height/2)+280),
#                 (frame_width-350,frame_height),
#                 (int(frame_width/2)-300,int(frame_height/2)-20),
#                 (int(frame_width/2)-200,int(frame_height/2)-50),
#                 ]

# 2
# Set coords for Streets, find Persons (Pedestrians)
def coords_CarInHouse(frame_width, frame_height):
	coords_polylines = np.array([
					[100,int(frame_height/2)-200], 
					[int(frame_width/2)+200,int(frame_height/2)-200], 
					[int(frame_width/2)+200,frame_height-200], 
					[100,frame_height-200]
					])
	coords_polygon = [
					(100,int(frame_height/2)-200), 
					(int(frame_width/2)+200,int(frame_height/2)-200), 
					(int(frame_width/2)+200,frame_height-200), 
					(100,frame_height-200)
					]
	return coords_polylines, coords_polygon

# 3
# Set coords for Streets, find Persons (Pedestrians)
def coords_Pedestrians(frame_width, frame_height):
	coords_polylines = np.array([
					[600,int(frame_height/2)], 
					[1250,int(frame_height/2)], 
					[830,frame_height-80], 
					[-100,frame_height-80]])
	coords_polygon = [
					(600, frame_height/2), 
					(1250, frame_height/2), 
					(830, frame_height-80), 
					(-100, frame_height-80)
				]
	return coords_polylines, coords_polygon

# 4
# Set coords for Freeways, find Cars (Overpass)
def coords_Freeways(frame_width, frame_height):
	coords_polylines = np.array([
					[440,int(frame_height/2)], 
					[610,int(frame_height/2)], 
					[500,frame_height], 
					[-140,frame_height]
					])
	coords_polygon = [
					(440, frame_height/2), 
					(610, frame_height/2), 
					(500, frame_height), 
					(-140, frame_height)
				]
	return coords_polylines, coords_polygon