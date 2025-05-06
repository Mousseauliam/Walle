from Modes import Auto,Follow,Manual,Sequence,Sleep
from Web import server
from Services.Mvt_walle import Walle
from Services.Modes_manager import ModeManager
from Web.log_redirector import init_socketio, redirect_stdout
import RPi.GPIO as GPIO

import threading
import time
import os

power=True

# Definition des pins
GPIO.setmode(GPIO.BCM)

pinBtn_R = 24
pinBtn_T = 2
pinBtn_C = 3
pinBtn_S = 23
state_btn=[0]*4


GPIO.setup(pinBtn_R, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pinBtn_C, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pinBtn_T, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pinBtn_S, GPIO.IN, pull_up_down = GPIO.PUD_UP)


#server
flask_thread = threading.Thread(target=server.run_web_server)
flask_thread.daemon = True
flask_thread.start()

robot = Walle("/dev/ttyACM0")
manager = ModeManager(robot,server)

#log redirection
init_socketio(server.socketio)
redirect_stdout()

# modes
modes = {
    "Auto": Auto,
    "Follow": Follow,
    "Manual": Manual,
    "Sequence": Sequence,
    "Sleep": Sleep
}

current_mode_name = None

while power:
    
    state_btn[0] = GPIO.input(pinBtn_R)
    state_btn[1] = GPIO.input(pinBtn_T)
    state_btn[2] = GPIO.input(pinBtn_C) 
    state_btn[3] = GPIO.input(pinBtn_S)
    #print(f"[Main] Button states: {state_btn}")
    
    selected = server.get_selected_mode()

    if selected != current_mode_name:
        print(f"[Main] Switching to mode: {selected}")
        current_mode_name = selected
        manager.stop_mode()
        if selected in modes:
            manager.launch_mode(modes[selected])
            
    if server.get_shudown():
        print("[Main] Shutdown command received.")
        power = False
            
    
    time.sleep(0.03)
    

manager.stop_mode()
#robot.sleep()
robot.close()

#os.system("sudo shutdown -h now")
