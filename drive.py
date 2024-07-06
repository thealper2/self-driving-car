import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import cv2
import socketio
import eventlet
import numpy as np

from tensorflow.keras.models import load_model
from flask import Flask
from PIL import Image
from io import BytesIO

from colorama import Fore, Back, Style
colorama.init(autoreset=True)
 
sio = socketio.Server()
 
app = Flask(__name__)

speed_limit = 10

def preprocess_img(img):
    img = img[60:135, :, :]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    return img / 255.0
 
@sio.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed'])
    img = Image.open(BytesIO(base64.b64decode(data['image'])))
    img = np.asarray(img)
    img = preprocess_img(img)
    img = np.array([img])
    steering_angle = float(model.predict(img))
    throttle = 1.0 - speed / speed_limit
    print('{} {} {}'.format(steering_angle, throttle, speed))
    send_control(steering_angle, throttle)
 
 
 
@sio.on('connect')
def connect(sid, environ):
    print(f'{Style.BRIGHT}{Back.RED}{Fore.WHITE}[+] Connected to the server')
    send_control(0, 0)
 
def send_control(steering_angle, throttle):
    sio.emit('steer', {
        'steering_angle': str(steering_angle),
        'throttle': str(throttle)
    })
 
 
if __name__ == '__main__':
    model = load_model('model.h5')
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)