from Modes import Auto,Follow,Manual,Sequence,Sleep
from Web import server
from Services.Mvt_walle import Walle
from Services.Modes_manager import ModeManager
from Web.log_redirector import init_socketio, redirect_stdout
import lgpio

import threading
import time
import os

power=True
fetch_git=False
sleep=False

# Definition des pins
h = lgpio.gpiochip_open(0)

pinBtn_R = 24
pinBtn_T = 2
pinBtn_C = 3
pinBtn_S = 23
state_btn=[0]*4
last_state_change =0


lgpio.gpio_claim_input(h, pinBtn_R, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(h, pinBtn_C, lgpio.SET_PULL_DOWN)
lgpio.gpio_claim_input(h, pinBtn_T, lgpio.SET_PULL_DOWN)
lgpio.gpio_claim_input(h, pinBtn_S, lgpio.SET_PULL_UP)


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

# music
music =["sunday_clothe", "la_vie_en_rose", "takes_a_moments"]
last_music =0

current_mode_name = None

while power:
    
    state_btn[0] = lgpio.gpio_read(h, pinBtn_R)
    state_btn[1] = lgpio.gpio_read(h, pinBtn_T)
    state_btn[2] = lgpio.gpio_read(h, pinBtn_C)
    state_btn[3] = lgpio.gpio_read(h, pinBtn_S)
    #print(f"[Main] Button states: {state_btn}")
    
    if ((time.time() -last_state_change)>0.5):
        if state_btn[0] == 0:
            robot.stop_sound()

        if state_btn[1] == 0:
            robot.sound(music[last_music])
            last_music += 1
            if last_music >= len(music):
                last_music = 0
            last_state_change = time.time()
            
    if state_btn[2] == 0:
        """
        print("[Main] sleep ...")
        if not sleep :
            robot.sleep()
            manager.stop_mode()
        else:
            robot.wake_up()
            manager.launch_mode(modes[current_mode_name])
        sleep = not sleep
        time.sleep(0.5)"""
        robot.sound("walle_oh_synth")
        
        
        
    if state_btn[3] == 0:
        print("btn soleil")
        power = False
        fetch_git = True
        
    
    
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
    

lgpio.gpiochip_close(h)
manager.stop_mode()
robot.sleep()
robot.close()
if fetch_git:
    print(fetch_git)
    os.system("systemctl --user restart walle.service")
#os.system("sudo shutdown -h now")
