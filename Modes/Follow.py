import time
from Vision.cam import Follow_factor

active = False

def run(robot,server):
    global active
    active = True
    x_deadzone=0.05
    turn_speed=0.2
    z_threshold=2.0
    z_deadzone=0.2
    speed=0.3
    deadzone = 0.09
    y_step = 0.01
    while active:
        factor=Follow_factor()

        if factor[1]>(z_threshold+z_deadzone) :
            robot.move(0.5+speed)
        
        elif factor[1]<(z_threshold-z_deadzone) :
            robot.move(0.5-speed)
        
        else:
            robot.move(0.5)
        
        neck_angle = robot.get_coef("neck_angle")
        if (factor[2] < (0.5 - deadzone)) and (neck_angle>y_step) :
            robot.neckAngle(round(neck_angle - y_step,2))
        elif (factor[2] > (0.5 + deadzone)) and (neck_angle<(1-y_step)) :
            robot.neckAngle(round(neck_angle + y_step,2))
                

        time.sleep(0.05)


def stop():
    global active
    active = False