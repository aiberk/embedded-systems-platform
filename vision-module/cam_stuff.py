import picamera2,time
import os,subprocess

LOC='all_imgs'


camera = picamera2.Picamera2()

def get_photo(preview = None):
    if preview is not None:
        preview_config= camera.create_preview_configuration(sensor={'output_size': (640, 480)})
        #full_config = camera.create_still_configuration(main={'size': (640, 480)})
        camera.configure(preview_config)
        camera.start_preview()
        camera.start()
        time.sleep(preview)

    camera.capture_file(path:=os.path.join(os.getcwd(), LOC, f'{str(time.time()).replace(".", "")}.jpg'))
    print(f'image saved to {path}')
    camera.stop_preview()

def __get_photo(preview = True):
    path=os.path.join(os.getcwd(), LOC, f'{str(time.time()).replace(".", "")}.jpg')
    #os.system(f'sudo libcamera-still -q 80 -n {int(not preview)} -o {path}')
    r= subprocess.Popen(f'sudo libcamera-still -q 80 -n {int(not preview)} -o {path}', shell=True).communicate()
    print(r)
    print(f'image saved to {path}')

if __name__ =='__main__':
    __get_photo()