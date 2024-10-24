import numpy as np

from pyvirtualcam import Camera, PixelFormat
from PIL import Image
import pyaudio, json

config = json.loads(open("config.json", "r").read())
images = { 
          key: np.asarray(Image.open(path).convert('RGBA').resize( tuple(config['camera_size']) ) ) for key, path in config['images'].items()
        }

# Getting loudness function from PWFace
def get_loudness(stream_local):
    data = stream_local.read(1024 * 3)
    numpy_data = np.frombuffer(data, dtype=np.int16)
    volume = np.abs(numpy_data).mean()
    return volume

p = pyaudio.PyAudio()
microphones = []
info = p.get_host_api_info_by_index(0)

# Microphone selecting
for i in range(p.get_device_count()):
    try:
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if (device_info.get('maxInputChannels')) > 0:
            print("Input Device ID: ", i, " - ",
                  device_info.get('name').encode('1251').decode('utf-8'))
            microphones.append(i)
    except:
        break

stream = p.open(format=pyaudio.paInt16, channels=1, rate=config['rate'], input=True, frames_per_buffer=config['chunk'],
                input_device_index=microphones[config['microphone_id']]) #Starting the audio stream

#Camera management
with Camera(width=config['camera_size'][0], height=config['camera_size'][1], fps=config['framerate'],
            backend="unitycapture", fmt=PixelFormat.RGBA, ) as cam:
    while True:
        loudness = get_loudness(stream)
        if loudness >= config['speaking_loudness']: # If user is speaking 
            cam.send(images['speaking']) # Send speaking face
        else:
            cam.send(images['idle']) # Send idle face
        cam.sleep_until_next_frame()

# Developed by Bream.