# Main parameteres and variables
from easydict import EasyDict as edict
# from core_utils.detect_loitering import loitering_people, coords_PeopleInSquare
import os

__C = edict()
cfg = __C

# PROCESS 
__C.PROCESS = edict()
__C.PROCESS.USE_GPU = False

# Percentage to change if posible to process service
__C.PROCESS.LIMIT_CPU = 90
# Remenber, in 01 second there are 30 frames, should by considered  
#   In 01 second, process 30 frames (images) ... really bad view, slow   -> Value is 1
#   In 01 second, process 01 frames (images) ... very  good view, fast   -> Value is 30
__C.PROCESS.NFRAMES = 10
# Number of seconds to run the Video Stream or Stream Cam
__C.PROCESS.RUN_NSECONDS = 90

# path local
GLOBAL_PATH = os.path.abspath(os.getcwd())
# path on opencv-server
# GLOBAL_PATH = '/var/www/webApp/webApp'

# FILES
__C.FILES = edict()
__C.FILES.GLOBAL_PATH = GLOBAL_PATH
# HANDLE IMAGES / VIDEOS
__C.FILES.MAX_CONTENT_LENGTH = 100 * 1024 * 1024
__C.FILES.UPLOAD_EXTENSIONS  = ["JPEG", "JPG", "PNG", "GIF", "MP4", "AVI"]
__C.FILES.UPLOAD_PATH_UP     = GLOBAL_PATH + '/files/uploads'
__C.FILES.UPLOAD_PATH_IN     = GLOBAL_PATH + '/files/input'
__C.FILES.UPLOAD_PATH_OUT    = GLOBAL_PATH + '/files/output'
__C.FILES.PATH_FIL_ALERTS    = GLOBAL_PATH + '/files/alerts'
__C.FILES.PATH_WEB_ALERTS    = 'files/alerts'
__C.FILES.PATH_OUT_FORWEB    = 'files/output'

# MAIL
__C.MAIL = edict()
# Email 01: From Gmail to Incabit - GI
__C.MAIL.GI_FROM_USERNAME = 'Admin Gmail'
__C.MAIL.GI_FROM_ADDRESS  = 'cesar.git.mdpp@gmail.com'
__C.MAIL.GI_FROM_PASSWORD = 'MPgit2020'
__C.MAIL.GI_TO_USERNAME   = 'CTO Incabit'
__C.MAIL.GI_TO_ADDRESS    = 'cesar@incabit.com'

# Email 02: From Incabit to User - IU
__C.MAIL.IU_FROM_USERNAME = 'CTO Incabit'
__C.MAIL.IU_FROM_ADDRESS  = 'cesar@incabit.com'
__C.MAIL.IU_FROM_PASSWORD = 'MPincabit28'

# MTCNN
__C.MTCNN = edict()
__C.MTCNN.PATH_MODEL = GLOBAL_PATH + '/models'
__C.MTCNN.CONFIDENCE = 0.80
__C.MTCNN.IMG_WIDTH  = 160
__C.MTCNN.IMG_HEIGHT = 160

# YOLO
__C.YOLO = edict()
  # YOLO ANALYTICS
__C.YOLO.V3_NAMES   = GLOBAL_PATH + '/core_yolo/data/coco.names'
__C.YOLO.V3_CFG     = GLOBAL_PATH + '/core_yolo/data/yolov3.cfg'
__C.YOLO.V3_WEIGHTS = GLOBAL_PATH + '/core_yolo/data/yolov3.weights'
__C.YOLO.CONFIDENCE = 0.3
__C.YOLO.THRESHOLD  = 0.3
__C.YOLO.SQUARESIZE = 416
  # YOLO DISTANCE
__C.YOLO.MIN_CONF = 0.40
__C.YOLO.NMS_THRESH = 0.40
    # boolean indicating if NVIDIA CUDA GPU should be used
__C.YOLO.USE_GPU = False
    # minimum safe distance (in pixels) that two people can be from each other
__C.YOLO.MIN_DISTANCE = 50