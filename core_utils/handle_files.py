from flask import Flask, render_template, request, make_response, jsonify, redirect
from werkzeug.utils import secure_filename
import os

# FILES FUNCTIONS
def allowed_file(file_name, file_extensions):
    if not "." in file_name :
        return False
    ext = file_name.rsplit(".", 1)[1]

    if ext.upper() in file_extensions:
        return True
    else:
        return False

def allowed_file_filesize(file_size, file_maxlength):
    if int(file_size) <= file_maxlength :
        return True
    else:
        return False
