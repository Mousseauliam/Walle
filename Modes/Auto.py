import time
from Vision.cam import get_factor
import random


def run(robot,server):
    deadzone = 0.09
    y_step = 0.01
    tilt_factor = 1
    active = True
    last_blink = 0
    wink_left = 0
    wink_right = 0
    eye_closed = False
    last_mvt=time.time()
    next_random=4
    
    while active:
        head_factor=get_factor()
        if all(element is not None for element in head_factor[:5]):
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
                    eye_closed = False
                case "blink":
                    if not eye_closed and (time.time() - last_blink) > 0.8:
                        robot.blink()
                        last_blink = time.time()
                        eye_closed = True
                    
                case "wink_left":
                    robot.manual("lid_L", 1)
                    robot.manual("lid_R", 0)
                    wink_left = time.time()
                case "wink_right":
                    robot.manual("lid_R", 1)
                    robot.manual("lid_L", 0)
                    wink_right = time.time()
        
            match head_factor[5]:
                case "brow_up":
                    robot.manual("eyebrow_L", 1)
                    robot.manual("eyebrow_R", 1)
                case "brow_down":
                    robot.manual("eyebrow_L", 0)
                    robot.manual("eyebrow_R", 0)
                case "brow_up_left":
                    robot.manual("eyebrow_L", 1)
                    robot.manual("eyebrow_R", 0)
                case "brow_up_right":
                    robot.manual("eyebrow_L", 0)
                    robot.manual("eyebrow_R", 1)
            last_mvt=time.time()
            next_random= random.uniform(4, 15)
        else :
            print('rien')
            if (time.time()-last_mvt)>next_random :
                print('maintenant')
                robot.neckAngle(max(0.3, min(robot.get_coef('neck_angle') + random.uniform(-0.1, 0.1), 1)))
                robot.neckLR(robot.get_coef('neck_LR') + random.uniform(-0.2, 0.2))
                last_mvt=time.time()
                next_random= random.uniform(4, 15)
            
        if head_factor[6] is not None:
            robot.emote(head_factor[6])
            
        time.sleep(0.01) 

def stop():
    global active
    active = False