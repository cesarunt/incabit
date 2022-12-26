from flask import Flask, Response, render_template, request, make_response, jsonify, redirect, url_for, send_file, send_from_directory
import urllib, urllib.request, requests
from flask_mail import Mail,  Message
import numpy as np
import imutils
import tensorflow as tf
import tensorflow.keras
import cv2
import timeit, time, datetime
import argparse, os, math, sys
# SETTING - Config
from setting.config import cfg
# MTCNN - Library for Use Mask detection
from core_mtcnn import MTCNN
# YOLO - Functions to process Object Detect
from core_yolo.main import *
# YOLO - Functions in general
from core_utils.detect_faces import detect_faces_with_mask
from core_utils.select_camera import get_camera
from core_utils.handle_files import allowed_file, allowed_file_filesize
from core_utils.handle_process import *
# Others librarys
from PIL import Image
from werkzeug.utils import secure_filename
# from shapely.geometry import Point, Polygon
# import threading
import subprocess
import psutil

app = Flask(__name__)

app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['MAX_CONTENT_LENGTH'] = cfg.FILES.MAX_CONTENT_LENGTH 
app.config['UPLOAD_EXTENSIONS']  = cfg.FILES.UPLOAD_EXTENSIONS
app.config['UPLOAD_PATH_UP']     = cfg.FILES.UPLOAD_PATH_UP
app.config['UPLOAD_PATH_IN']     = cfg.FILES.UPLOAD_PATH_IN
app.config['UPLOAD_PATH_OUT']    = cfg.FILES.UPLOAD_PATH_OUT
app.config['PATH_FIL_ALERTS']    = cfg.FILES.PATH_FIL_ALERTS
app.config['PATH_WEB_ALERTS']    = cfg.FILES.PATH_WEB_ALERTS
app.config['PATH_OUT_FORWEB']    = cfg.FILES.PATH_OUT_FORWEB

# HOME
@app.route('/')
def home():
    return render_template('home.html')

# DASHBOARD
@app.route('/ai/')
def ai_home():
    # Percentage CPU usage
    _,_ = get_useProcess_CPU()
    return render_template('ai_home.html')

# AI HEALTH
@app.route('/ai/healthy')
def ai_healthy():
    # Percentage CPU usage
    _,_ = get_useProcess_CPU()
    return render_template('ai_healthy.html')

# AI TRANSPORT
@app.route('/ai/transport')
def ai_transport():
    # Percentage CPU usage
    _,_ = get_useProcess_CPU()
    return render_template('ai_transport.html')

# AI SAFECITY
@app.route('/ai/safety')
def ai_safety():
    # Percentage CPU usage
    _,_ = get_useProcess_CPU()
    return render_template('ai_safety.html')

# AI USE MASK
@app.route('/ai_mask')
def ai_mask():
    # getting CPU usage to show the service AI ...
    result = get_viewService_CPU('ai_mask.html')
    return result

# AI SOCIAL DISTANCE
@app.route('/ai/distance')
def ai_distance():
    # getting CPU usage to show the service AI ...
    result = get_viewService_CPU('ai_distance.html')
    return result

# AI VIDEO ANALYTICS
@app.route('/ai_analytics')
def ai_analytics():
    # getting CPU usage to show the service AI ...
    result = get_viewService_CPU('ai_analytics.html')
    return result

# AI SETTING
@app.route('/ai_setting')
def ai_setting():
    # Percentage CPU usage
    _,_ = get_useProcess_CPU()
    return render_template('ai_setting.html', 
                            use_GPU=cfg.PROCESS.USE_GPU, limit_CPU=cfg.PROCESS.LIMIT_CPU, nFrames=cfg.PROCESS.NFRAMES, nSeconds=cfg.PROCESS.RUN_NSECONDS,
                            mtcnn_conf=cfg.MTCNN.CONFIDENCE, mtcnn_width=cfg.MTCNN.IMG_WIDTH, mtcnn_height=cfg.MTCNN.IMG_HEIGHT,
                            yolo_conf=cfg.YOLO.CONFIDENCE, yolo_thres = cfg.YOLO.THRESHOLD
                        )

# AI ACTION VIDEO AND STREAM
@app.route("/action_processStream", methods=["GET", "POST"])
def action_processStream():
    active_show = "active show"
    result = False
    if request.method == "POST":
        global vs, mask_streamOut, mask_streamAlert, _analytic, _object
        (mask_streamOut, mask_streamAlert) = ("", False)
        # get values of media and service    -> (stream or ai_service)
        media = request.form.get('media_stream')
        service = request.form.get('service_stream')
        # Verify if posible to process
        if get_viewProcess_CPU() is True :
            if service == 'ai_analytics':
                _analytic = request.form.get('analyticStream_selected')
                _object = request.form.get('objectStream_selected')
                # get value of selected camera
                camera_name = request.form.get('camera_selected')
                if (camera_name=="cam_none"):
                    mask_streamAlert = "Debe seleccionar una cámara"
                elif (_analytic=="analytic_none"):
                    mask_streamAlert = "Debe seleccionar una analítica"
                elif (_object=="none"):
                    mask_streamAlert = "Debe seleccionar un objeto"
                else:
                    # get URL from selected camera
                    url = get_camera(camera_name)
                    # start stream or load video
                    vs = cv2.VideoCapture(url)
                    if (vs.isOpened()==True):
                        mask_streamOut = media
                        result = True
                    else:
                        mask_streamAlert = "Error: No se pudo conectar con la cámara"
            if service == 'ai_distance':
                # get value of selected camera
                camera_name = request.form.get('camera_selected')
                if (camera_name=="cam_none"):
                    mask_streamAlert = "Debe seleccionar una cámara"
                else:
                    # get URL from selected camera
                    url = get_camera(camera_name)
                    # start stream or load video
                    vs = cv2.VideoCapture(url)
                    if (vs.isOpened()==True):
                        mask_streamOut = media
                        result = True
                    else:
                        mask_streamAlert = "Error: No se pudo conectar con la cámara"
            if service == 'ai_loitering':
                # get value of selected camera
                print("loitering...")
                camera_name = request.form.get('camera_selected')
                if (camera_name=="cam_none"):
                    mask_streamAlert = "Debe seleccionar una cámara"
                else:
                    # get URL from selected camera
                    url = get_camera(camera_name)
                    # start stream or load video
                    vs = cv2.VideoCapture(url)
                    if (vs.isOpened()==True):
                        mask_streamOut = media
                        result = True
                    else:
                        mask_streamAlert = "Error: No se pudo conectar con la cámara"
        else:
            mask_streamAlert = "El servidor está procesando, debe esperar un momento."

        return render_template(str(service)+'.html', mask_streamOut=mask_streamOut, mask_streamAlert=mask_streamAlert, active_image="", active_video="", active_stream=active_show)


@app.route("/action_processImage", methods=["GET", "POST"])
def action_processImage():
    active_show = "active show"

    if request.method == "POST":
        global vs, file_image, mask_imageOut, mask_imageAlert, _analytic, _object
        (mask_imageOut, mask_imageAlert) = ("", False)
        # get values of media and service    -> (video/stream or ai_mask/ai_service)
        media = request.form.get('media_image')
        service = request.form.get('service_image')

        if service == "ai_mask" :
            # Verify if posible to process
            if get_viewProcess_CPU() is True :
                mask_imageIn = os.path.join(app.config['UPLOAD_PATH_IN'], file_image)
                # file_upload.save(mask_imageIn)
                # Call generate function to process image output 'file_out'
                if generate_mask_image(file_image) is True:
                    mask_imageOut = os.path.join(app.config['PATH_OUT_FORWEB'], ("um_"+file_image))
                else:
                    mask_imageAlert = "Error: No se pudo procesar la imagen"      
            else:
                mask_imageAlert = "El servidor está procesando, debe esperar un momento."

        if service == "ai_distance" :
            # Verify if posible to process
            if get_viewProcess_CPU() is True :
                # mask_imageIn = os.path.join(app.config['UPLOAD_PATH_IN'], file_image)
                # file_upload.save(mask_imageIn)
                # Call generate function to process image output 'file_out'
                # 0. Set path_in 
                # path_in = app.config['UPLOAD_PATH_IN']
                # 1. Read image from file
                image = cv2.imread(os.path.join(app.config['UPLOAD_PATH_IN'], file_image))
                (H, W) = image.shape[:2]
                # [-] generate distance image()
                image_result = generateImage_socialDistance(image, W, H)
                # Get path to save image result
                path_save = app.config['UPLOAD_PATH_OUT']

                if image_result is not None :
                    # Saving the image on ../files/output
                    save_image = cv2.imwrite(path_save+"/sd_"+file_image, image_result)
                    if save_image is True:
                        mask_imageOut = os.path.join(app.config['PATH_OUT_FORWEB'], ("sd_"+file_image))
                    else:
                        mask_imageAlert = "Error: No se pudo procesar la imagen"  
                else:
                    mask_imageAlert = "No fue posible procesar la imagen"
            else:
                mask_imageAlert = "El servidor está procesando, debe esperar un momento."

        if service == "ai_analytics" :
            # Verify if posible to process
            if get_viewProcess_CPU() is True :
                # Saving the input image on ../files/input
                # mask_imageIn = os.path.join(app.config['UPLOAD_PATH_IN'], file_image)
                # file_upload.save(mask_imageIn)
                # Call generate function to process image output 'file_out'
                # 0. Set path_in 
                # path_in = app.config['UPLOAD_PATH_IN']
                # 1. Read image from file
                image = cv2.imread(os.path.join( app.config['UPLOAD_PATH_IN'],file_image))
                (H, W) = image.shape[:2]
                # [-] Generate analytic image()
                # Validate by type of analytic
                localConfidence = cfg.YOLO.CONFIDENCE
                if _analytic=="analytic_detectO":
                    image_result = generateImage_analyticsDetectObjects(image, W, H, localConfidence)
                    sub = "do_"
                if _analytic=="analytic_searchO":
                    image_result = generateImage_analyticsDetectObjects(image, W, H, localConfidence, _object)
                    sub = "so_"
                # if _analytic=="analytic_loiterP":
                #     image_result = generateImage_loiteringDetectObjects(image, W, H, localConfidence, _object)
                #     sub = "lo_"
                if _analytic=="analytic_countP":
                    image_result = generateImage_analyticsCountPersons(image, W, H, localConfidence)
                    sub = "cp_"
                
                if image_result is not None :
                    # Saving the image on ../files/output
                    save_image = cv2.imwrite(app.config['UPLOAD_PATH_OUT']+"/"+sub+file_image, image_result)
                    if save_image is True:
                        mask_imageOut = os.path.join(app.config['PATH_OUT_FORWEB'], (sub+file_image))
                    else:
                        mask_imageAlert = "Error: No se pudo procesar la imagen"  
                else:
                    mask_imageAlert = "No fue posible procesar la imagen"
            else:
                mask_imageAlert = "El servidor está procesando, debe esperar un momento."
                
        return render_template(str(service)+'.html', mask_imageOut=mask_imageOut, mask_imageAlert=mask_imageAlert, active_image=active_show, active_video="", active_stream="")


@app.route("/action_processVideo", methods=["GET", "POST"])
def action_processVideo():
    active_show = "active show"

    if request.method == "POST":
        global vs, file_video, mask_videoOut, mask_videoAlert, _analytic, _object
        (mask_videoOut, mask_videoAlert) = ("", False)
        # get values of media and service    -> (video/stream or ai_mask/ai_service)
        media = request.form.get('media_video')
        service = request.form.get('service_video')

        # get values fron file upload
        file = request.files["file_video"]
        file_video = file.filename
        # get vales from _analytic and _objects
        _analytic = request.form.get('analyticVideo_selected')
        _object = request.form.get('objectVideo_selected')

        # Verify if posible to process
        if get_viewProcess_CPU() is True :
            # get URL from selected camera
            url = os.path.join(app.config['UPLOAD_PATH_UP'], file_video)
            # start stream or load video
            vs = cv2.VideoCapture(url)
            if (vs.isOpened()==True):
                mask_videoOut = media
            else:
                mask_videoAlert = "Error: No se pudo cargar el " + str(media)
        else:
            mask_videoAlert = "El servidor está procesando, debe esperar un momento."

        return render_template(str(service)+'.html', mask_videoOut=mask_videoOut, mask_videoAlert=mask_videoAlert, active_image="", active_video=active_show, active_stream="")


# AI SOCIAL DISTANCE - METHOD POST
@app.route('/ai_distance', methods=['POST'])
def ai_distance_form():
    global file_image, file_video
    active_show = "active show"

    if request.method == "POST":
        # Validate type of process: IMAGE - VIDEO - STREAM
        process = request.values.get("process")

        if process == "video" or process =="image":
        
            if "filesize" in request.cookies:
                if not allowed_file_filesize(request.cookies["filesize"], app.config["MAX_CONTENT_LENGTH"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)
                file = request.files["file"]
                filesize = request.cookies.get("filesize")

                if file.filename == "":
                    print("No filename")
                    return redirect(request.url)
                if int(filesize) > 0 :
                    res = make_response(jsonify({"message": f"El archivo {file.filename} fue cargado con éxito."}), 200)
                    print("File uploaded")
                    upload = True
                if allowed_file(file.filename, app.config["UPLOAD_EXTENSIONS"]):
                    filename = secure_filename(file.filename)
                    # file.save(os.path.join(app.config["UPLOAD_PATH_UP"], filename))
                    if process == "video":
                        file.save(os.path.join(app.config["UPLOAD_PATH_UP"], filename))
                        file_video = filename
                    if process == "image":
                        file.save(os.path.join(app.config["UPLOAD_PATH_IN"], filename))
                        file_image = filename
                    print("File saved")
                    file_video = filename
                    if (upload == True):
                        return res
                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

@app.route("/ai_distance_stream")
def ai_distance_stream():
    return Response(ai_distance_streaming(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

def ai_distance_streaming():
    # grab global references to the video stream, output frame, and lock variables
    global vs, outputFrame
    (W, H) = (None, None)
    outputFrame = None
    # print("[*] Processing video ...")

    vs_width  = int(vs.get(3))
    vs_height = int(vs.get(4))
    vs_rotate = False

    if vs_width > vs_height :
        vs_rotate = True

    i = 0
    print("Start streaming...")
    while True:
        # Call generate function to process image output 'file_out'
        # 0. Set path_in
        frameId = vs.get(1) #current frame number

        # 1. Read image from video's frame
        (grabbed, image) = vs.read()
        if not grabbed: break
        # if vs_rotate==True :
    	#     image = cv2.transpose(image)

        if W is None or H is None:
            (H, W) = image.shape[:2]
        
        if (frameId % math.floor(cfg.PROCESS.NFRAMES) == 0):
            # [-] generate analytics image()
            image_result = generateImage_socialDistance(image, W, H)

            if image_result is not None :
                outputFrame = image_result
            else:
                outputFrame = image
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            i += 1
            print(str(i))
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
            
        if i == cfg.PROCESS.RUN_NSECONDS + 1:
            print("...Stop streaming")
            vs.release()
            break


# AI VIDEO ANALYTICS - METHOD POST
@app.route('/ai_analytics', methods=['POST'])
def ai_analytics_form():
    global _analytic, _object, file_image, file_video
    active_show = "active show"
    # analytic (objects, persons, others)
    _analytic = request.form.get('analytic')
    _object = request.form.get('object')

    if request.method == "POST":
        # Validate type of process: IMAGE - VIDEO - STREAM
        process = request.values.get("process")

        if process == "video" or process == "image" :
        
            if "filesize" in request.cookies:
                if not allowed_file_filesize(request.cookies["filesize"], app.config["MAX_CONTENT_LENGTH"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)
                file = request.files["file"]
                filesize = request.cookies.get("filesize")

                if file.filename == "":
                    print("No filename")
                    return redirect(request.url)
                if int(filesize) > 0 :
                    res = make_response(jsonify({"message": f"El archivo {file.filename} fue cargado con éxito."}), 200)
                    print("File uploaded")
                    upload = True
                if allowed_file(file.filename, app.config["UPLOAD_EXTENSIONS"]):
                    filename = secure_filename(file.filename)
                    # file.save(os.path.join(app.config["UPLOAD_PATH_UP"], filename))
                    if process == "video":
                        file.save(os.path.join(app.config["UPLOAD_PATH_UP"], filename))
                        file_video = filename
                    if process == "image":
                        file.save(os.path.join(app.config["UPLOAD_PATH_IN"], filename))
                        file_image = filename
                    print("File saved")
                    file_video = filename
                    if (upload == True):
                        return res
                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

# AI ANALYTICS OBJECTS - STREAM
@app.route("/ai_analytics_stream")
def ai_analytics_stream():
    global _analytic, _object
    return Response(ai_analytics_streaming(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

def ai_analytics_streaming():
    global vs, outputFrame, _analytic, _object
    (W, H) = (None, None)
    outputFrame = None

    vs_width  = int(vs.get(3))
    vs_height = int(vs.get(4))
    
    nf = 0
    loiter_dict = { 'loiter_numperson' : 0,
                    'loiter_band'      : False,
                    'loiter_timeI'     : 0.0,
                    'loiter_timeE'     : 0.0,
                    'loiter_text_alert': "",
                    'loiter_i'         : 0,
                    'loiter_j'         : 0
                }

    # print("Start streaming...")
    while True:
        # Call generate function to process image output 'file_out'
        # 0. Set path_in        
        frameId = vs.get(1) #current frame number
        # 1. Read image from video's frame
        (grabbed, image) = vs.read()
        if not grabbed: break

        if W is None or H is None:
            (H, W) = image.shape[:2]
        
        if (frameId % math.floor(cfg.PROCESS.NFRAMES) == 0):
            # Validate by type of analytic
            localConfidence = cfg.YOLO.CONFIDENCE
            if _analytic=="analytic_detectO":
                image_result = generateImage_analyticsDetectObjects(image, W, H, localConfidence)
            if _analytic=="analytic_searchO":
                image_result = generateImage_analyticsDetectObjects(image, W, H, localConfidence, _object)
            if _analytic=="analytic_countP":
                image_result = generateImage_analyticsCountPersons(image, W, H, localConfidence)
            if _analytic=="analytic_loiterP":
                loiter_dict, image_result = generateImage_loiteringDetectObjects(image, W, H, localConfidence, app.config['PATH_FIL_ALERTS'], loiter_dict, _object)

            if image_result is not None :
                outputFrame = image_result
            else:
                outputFrame = image
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            nf += 1
            # print(str(nf))

            # ensure the frame was successfully encoded
            if not flag:
                continue

            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
        
        if nf == cfg.PROCESS.RUN_NSECONDS + 1:
            print("...Stop streaming")
            vs.release()
            break

# AI USE MASK - STREAM
@app.route("/ai_mask_stream")
def ai_mask_stream():
    return Response(ai_mask_streaming(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/ai_close_stream/<source>")
def ai_close_stream(source):
    global vs
    vs.release()
    url = "/" + source
    return redirect(url)

def ai_mask_streaming():
    global vs, outputFrame
    (W, H) = (None, None)
    outputFrame = None

    # Variables de configuración
    IMG_WIDTH = cfg.MTCNN.IMG_WIDTH  # Ancho de la mascara que recore la imagen
    IMG_HEIGHT = cfg.MTCNN.IMG_HEIGHT # Alto de la mascara que recore la imagen
    BBOX_PERCENTAGE = 0.02 # Porcentage de ampliación del bounding box
    CONFIDENCE = cfg.MTCNN.CONFIDENCE # Porcentage de confidencia del detector de rostros
    classes = ['no_mask', 'mask'] # Clases de la capa final

    vs_width  = int(vs.get(3))
    vs_height = int(vs.get(4))
    vs_rotate = False

    if vs_width > vs_height :
        vs_rotate = True

    # Creado el modelo de detección de rostros (Multi-Task Cascaded Convolutional Neural Network)
    face_detector = MTCNN()
    # Creando el modelo de detección de mascaras (MaskNet)
    model_keras = tf.keras.models.load_model(cfg.MTCNN.PATH_MODEL+'/mask_net.hdf5', compile=False)

    i = 0
    # print("Start streaming...")
    while True:
        frameId = vs.get(1) #current frame number
        _, frame = vs.read()

        if frame is None: break
        # if vs_rotate==True :
    	#     frame = cv2.transpose(frame)
        
        # resize the frame and then detect people (and only people) in it
        frame = imutils.resize(frame, width=800)
        
        if W is None or H is None:
            (H, W) = frame.shape[:2]
        
        if (frameId % math.floor(cfg.PROCESS.NFRAMES) == 0):
            img_color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_color_temp = detect_faces_with_mask(img_color, face_detector, model_keras, classes, CONFIDENCE, 
                                bbox_percentage=BBOX_PERCENTAGE, predictor='keras', target_size=(IMG_WIDTH, IMG_HEIGHT))
            
            image_result = cv2.cvtColor(img_color_temp, cv2.COLOR_RGB2BGR)

            if image_result is not None :
                outputFrame = image_result
            else:
                outputFrame = img_color
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            i += 1
            print(str(i))

            # ensure the frame was successfully encoded
            if not flag:
                continue

            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
        
        if i == cfg.PROCESS.RUN_NSECONDS + 1 :
            print("...Stop streaming")
            vs.release()
            break

# AI USE MASK - METHOD POST
@app.route('/ai_mask', methods=['POST'])
def ai_mask_form():
    global file_image, file_video
    active_show = "active show"

    if request.method == "POST":
        # Validate type of process: IMAGE - VIDEO - STREAM
        process = request.values.get("process") 

        if process == "video" or process =="image":
        
            if "filesize" in request.cookies:
                if not allowed_file_filesize(request.cookies["filesize"], app.config["MAX_CONTENT_LENGTH"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)
                file = request.files["file"]
                filesize = request.cookies.get("filesize")

                if file.filename == "":
                    print("No filename")
                    return redirect(request.url)
                if int(filesize) > 0 :
                    res = make_response(jsonify({"message": f"El archivo {file.filename} fue cargado con éxito."}), 200)
                    print("File uploaded")
                    upload = True
                if allowed_file(file.filename, app.config["UPLOAD_EXTENSIONS"]):
                    filename = secure_filename(file.filename)
                    if process == "video":
                        file.save(os.path.join(app.config["UPLOAD_PATH_UP"], filename))
                        file_video = filename
                    if process == "image":
                        file.save(os.path.join(app.config["UPLOAD_PATH_IN"], filename))
                        file_image = filename
                    print("File saved")
                    if (upload == True):
                        return res

                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

# AI USE MASK - IMAGE FILES FUNCTIONS
@app.route('/files/input/<filename>')
def ai_mask_in(filename):
    return send_from_directory(app.config['UPLOAD_PATH_IN'], filename)

@app.route('/files/output/<filename>')
def ai_mask_out(filename):
    return send_from_directory(app.config['UPLOAD_PATH_OUT'], filename)

@app.route('/files/alerts/<filename>')
def ai_files_alerts(filename):
    return send_from_directory(app.config['PATH_FIL_ALERTS'], filename)

@app.route('/files/alerts/mdb/<filename>')
def ai_files_alerts_mdb(filename):
    return send_from_directory(os.path.join(app.config['PATH_FIL_ALERTS'],"mdb"), filename)

# AI USE MASK - IMAGE FUNCTIONS
def get_size_image(filename):
    # Detectando las mascaras en la imagen (MaskNet)
    img = cv2.imread(filename)
    (H, W) = img.shape[:2]
    return W, H

def generate_mask_image(filename):
    # grab global references to the output frame and lock variables
    global outputFrame

    path_in = app.config['UPLOAD_PATH_IN']
    outputFrame = None
    # Calculando el tiempo
    start_time = time.time()
    # print("[*] Generating image ...")
    # Variables de configuración
    IMG_WIDTH = cfg.MTCNN.IMG_WIDTH # Ancho de la imagen
    IMG_HEIGHT = cfg.MTCNN.IMG_HEIGHT # Alto de la imagen
    BBOX_PERCENTAGE = 0.02 # Porcentage de ampliación del bounding box
    CONFIDENCE = cfg.MTCNN.CONFIDENCE # Porcentage de confidencia del detector de rostros
    classes = ['no_mask', 'mask'] # Clases de la capa final
    # Creado el modelo de detección de rostros (Multi-Task Cascaded Convolutional Neural Network)
    face_detector = MTCNN()
    # Creando el modelo de detección de mascaras (MaskNet)
    model_keras = tf.keras.models.load_model(cfg.MTCNN.PATH_MODEL+'/mask_net.hdf5', compile=False)
    # Detectando las mascaras en la imagen (MaskNet)
    img = cv2.imread(os.path.join(app.config['UPLOAD_PATH_IN'], filename))
    #img = imutils.resize(img, width=1280)
    (H, W) = img.shape[:2]
    img_color = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    image_mask_detection = detect_faces_with_mask(img_color, face_detector, model_keras, classes, CONFIDENCE, 
                            bbox_percentage=BBOX_PERCENTAGE, predictor='keras', target_size=(IMG_WIDTH, IMG_HEIGHT))
    image = cv2.cvtColor(image_mask_detection, cv2.COLOR_RGB2BGR)

    outputFrame = image.copy()
    
    return save_image(app.config['UPLOAD_PATH_OUT'], filename, outputFrame)

def save_image(path_save, filename, img):
    # Saving the image 
    status = cv2.imwrite(path_save+"/um_"+filename, img)
    return status

@app.route("/ai_close_image/<source>")
def ai_close_image(source):
    url = "/" + source
    return redirect(url)

@app.route("/ai_save_image", methods=["POST"])
def ai_save_image():

    if request.method == "POST":
        down_image = request.form.get('down_image')
        
    return send_file(down_image, as_attachment=True)

# HOME MAIL - METHOD POST
@app.route('/', methods=['POST'])
def home_form():
    if request.method == "POST":
        # Get values of Form
        IU_TO_USERNAME = request.values.get("mail_username")
        IU_TO_ADDRESS  = request.values.get("mail_address")
        IU_TO_MESSAGE  = request.values.get("mail_message")
        IU_TO_PHONENUMBER  = request.values.get("mail_phonenumber")

        with app.app_context():
            # Email 01: From Gmail to Incabit - GI
            app.config['MAIL_SERVER']='smtp.gmail.com'
            app.config['MAIL_PORT'] = 465
            app.config['MAIL_USE_TLS'] = False
            app.config['MAIL_USE_SSL'] = True
            app.config['MAIL_USERNAME'] = cfg.MAIL.GI_FROM_ADDRESS
            app.config['MAIL_PASSWORD'] = cfg.MAIL.GI_FROM_PASSWORD
            email01 = Mail(app)
            msg01 = Message(
                        subject    = cfg.MAIL.GI_TO_USERNAME +", fuiste contactado por "+ IU_TO_USERNAME,
                        sender     = cfg.MAIL.GI_FROM_USERNAME +"<"+ cfg.MAIL.GI_FROM_ADDRESS +">",
                        recipients = [cfg.MAIL.GI_TO_USERNAME +"<"+cfg.MAIL.GI_TO_ADDRESS+">"],
                        body       = "Mensaje enviado por "+IU_TO_USERNAME+
                                     "\nCorreo electrónico:  "+IU_TO_ADDRESS +
                                     "\nNúmero telefónico:   "+IU_TO_PHONENUMBER +
                                     "\nMensaje:\n" + IU_TO_MESSAGE +
                                     "\n\nEs importante responder a la brevedad posible.\nSaludos cordiales"
                        )
            try:
                print("sending mail")
                email01.send(msg01)
            except:
                print("Oops!", sys.exc_info()[0], ".")
            
            res = make_response(jsonify({
                "message" : f"Mensaje enviado con éxito, en breve te contactaremos mediante el número telefónico ingresado o a través de tu correo electrónico ",
                "add" : f"{IU_TO_ADDRESS}"
            }), 200)
            print("Mail Sent")
            return res    

# INIT
# ====
if __name__ == '__main__':
    # start the flask app
    app.run(debug=True, use_reloader=True)
    #app.run(host="0.0.0.0", port="5000", debug=True, threaded=True, use_reloader=True)