from picamera2 import Picamera2,Preview
import time,os
from deepface import DeepFace

def take_photo(preview_time= 0):
	picam2= Picamera2()
	preview= Preview.NULL
	if preview_time is not None:
		camera_config= picam2.create_preview_configuration()
		picam2.configure(camera_config)
	
		picam2.start_preview(Preview.QTGL)
		picam2.start()
		time.sleep(preview_time)
	
	else:
		picam2.start_preview(Preview.NULL)
		picam2.start()
		
	picam2.capture_file(f_name:=f'''{str(time.time()).replace('.','')}.jpg''')
	print(f_name)
	return f_name
	
def detect_image(f_name):
	detector = 'yolov8'
	d= DeepFace.extract_faces(img_path= f_name, detector_backend= detector,align=True)
	return len(d)
	

def detect_emotions(f_name):
	detector = 'yolov8'
	#detector= 'fastmtcnn'
	#detector= 'centerface'
	d= DeepFace.analyze(img_path= f_name, actions= ['emotion'], detector_backend=detector)
	print(d)
	return d
	
def run_proc():
	img = take_photo(2)
	emotions = detect_emotions(img)
	print('final emotions')
	t = [i['dominant_emotion'] for i in emotions]
	print(t)
	return t
	
if __name__ =='__main__':
	'''take_photo(None)'''
	'''cam-env'''
	#detect_emotions()
	#take_photo()
	#sudo reboot when first attaching camera
	#need test_mqtt_controller.py
	#detect_emotions('the_guys.jpg')
	run_proc()
