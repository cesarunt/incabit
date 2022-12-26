import os

def get_camera(cam_value, file_name=None, path=None):

    url = None
    if file_name is None:
        if cam_value == "cam_home_web":
            url = 0
        if cam_value == "cam_home_living":
            url = "rtsp://admin:MPexir28@192.168.0.14:554/media/video1"
        if cam_value == "cam_pp_mainsquare":
            url = "rtsp://admin:admin123456@209.45.63.238:554/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46YWRtaW4xMjM0NTY="
        if cam_value == "cam_pp_backdoor":
            url = "rtsp://admin:Admin123@209.45.63.238:554/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM="
    else:
        url = os.path.join(path, file_name)

    return url