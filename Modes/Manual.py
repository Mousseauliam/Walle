import time

active = False

def run(robot,server):
    global active
    active = True
    dump = server.get_last_command()
    dump = server.get_selected_emote()
    dump = server.get_servo_data()
    
    #commentaire
    
    while active:
        command = server.get_last_command()
        if command!= None:
            print(f"[Manual] Command received:{command}")
            match command:
                case "left":
                    robot.turn(0.2)
                case "right":
                    robot.turn(0.8)
                case "forward":
                    robot.move(0.9)
                case "backward":
                    robot.move(0.1)
                case "stop":
                    robot.move(0.5)
                case "blink":
                    robot.blink()
                
        emote = server.get_selected_emote()
        if emote != None:
            print(f"[Manual] Emote received: {emote}")
            robot.emote(emote)
            
        servo, position = server.get_servo_data()
        if servo != None:
            match servo:
                case 'head_angle':
                    robot.headAngle(position)
                case "neck_level":
                    robot.neckLevel(position)
                case "neck_angle":
                    robot.neckAngle(position)
                case "sadness":
                    robot.sadness(position)
                case "neck_LR":
                    robot.neckLR(position)
                case "eyebrows":
                    robot.eyebrow(position)
                case "speed":
                    robot.move(position)
                case _:
                    print(f"[Manual] Servo {servo} to position {position}")
                    robot.manual(servo,position)
            
        time.sleep(0.05)

def stop():
    global active
    active = False
