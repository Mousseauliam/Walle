import time
from Vision.cam import get_head_factor

active = False

deadzone = 0.08
y_step = 0.02
x_factor = 0.5
tilt_factor = 1.0

def run(robot,server):
    global active
    active = True
    while active:
        head_factor=get_head_factor()
        if head_factor is not None:
            print(f"[Auto] Head factor: {head_factor}")
            
            neck_angle = robot.get_coef("neck_angle")
            if (head_factor[1] < (0.5 - deadzone)) and (neck_angle>y_step) :
                robot.neckAngle(round(neck_angle - y_step,2))
            elif (head_factor[1] > (0.5 + deadzone)) and (neck_angle<(1-y_step)) :
                robot.neckAngle(round(neck_angle + y_step,2))
                
            neck_LR = robot.get_coef("neck_LR")
            neck_LR_temp = round((head_factor[0] - 0.5) * x_factor + 0.5,2)
            if (neck_LR!= neck_LR_temp):
                robot.neckLR(neck_LR_temp)

            head_angle = robot.get_coef("head_angle")
            head_angle_temp = round((head_factor[2] - 0.5) * tilt_factor + 0.5,2)
            if (head_angle!= head_angle_temp):
                robot.headAngle(head_angle_temp)

            time.sleep(0.1) 

def stop():
    global active
    active = False