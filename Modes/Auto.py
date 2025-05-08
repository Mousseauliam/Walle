import time
from Vision.cam import get_head_factor

active = False

deadzone = 0.09
y_step = 0.03
tilt_factor = 1.2

global last_blink
global wink_left
global wink_right 
global cooling_time
global eye_closed


def run(robot,server):
    global active, last_blink, wink_left, wink_right, cooling_time, eye_closed
    active = True
    last_blink = 0
    wink_left = 0
    wink_right = 0
    cooling_time = 0.5
    eye_closed = False
    
    while active:
        head_factor=get_head_factor()
        if head_factor is not None:
            neck_angle = robot.get_coef("neck_angle")
            if (head_factor[1] < (0.5 - deadzone)) and (neck_angle>y_step) :
                robot.neckAngle(round(neck_angle - y_step,2))
            elif (head_factor[1] > (0.5 + deadzone)) and (neck_angle<(1-y_step)) :
                robot.neckAngle(round(neck_angle + y_step,2))
                
            neck_LR = robot.get_coef("neck_LR")
            x_factor = (head_factor[2] + 0.02) * (0.3 - 0.5) / (-0.07 + 0.02) + 0.5
            neck_LR_temp = round((head_factor[0] - 0.5) * x_factor+ 0.5,2)
            if (neck_LR!= neck_LR_temp):
                robot.neckLR(neck_LR_temp)

            head_angle = robot.get_coef("head_angle")
            head_angle_temp = round(((1-head_factor[3]) - 0.5) * tilt_factor + 0.5,2)
            if (head_angle!= head_angle_temp):
                robot.headAngle(head_angle_temp)
                
            match head_factor[4]:
                case "open":
                    if (time.time() - wink_left) > 0.4:
                        robot.manual("lid_L", 0)
                    if (time.time() - wink_right) > 0.4:
                        robot.manual("lid_R", 0)
                case "blink":
                    if not eye_closed and (time.time() - last_blink) > 0.8:
                        robot.blink()
                        last_blink = time.time()
                        eye_closed = True
                    else:
                        eye_closed = False
                    
                case "wink_left":
                    robot.manual("lid_L", 1)
                    robot.manual("lid_R", 0)
                    wink_left = time.time()
                case "wink_right":
                    robot.manual("lid_R", 1)
                    robot.manual("lid_L", 0)
                    wink_right = time.time()
            
            time.sleep(0.1) 

def stop():
    global active
    active = False