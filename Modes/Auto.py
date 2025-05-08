import time
from Vision.cam import get_head_factor

active = False

deadzone = 0.09
y_step = 0.03
tilt_factor = 1.2

last_blink = 0
wink_left = False
wink_right = False

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
            print( head_factor[2])
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
                    if not wink_left :
                        robot.manual("lid_L", 0)
                    if not wink_right :
                        robot.manual("lid_R", 0)
                case "blink":
                    if (time.time() - last_blink) > 0.5:
                        robot.blink()
                        last_blink = time.time()
                case "wink_left":
                    robot.manual("lid_L", 1)
                    robot.manual("lid_R", 0)
                    wink_left = True
                case "wink_right":
                    robot.manual("lid_R", 1)
                    robot.manual("lid_L", 0)
                    wink_right = True
            
            time.sleep(0.1) 

def stop():
    global active
    active = False