import time
import random

def auto_adjust(walle):
    walle.headAngle(0.5)
    walle.coef['UD_R'] = 0
    walle.update(['UD_R'])
    time.sleep(1)
    walle.coef['UD_L'] = 0
    walle.update(['UD_L'])
    time.sleep(1)
    walle.sadness(0)
    time.sleep(1)
    walle.blink()
    time.sleep(0.7)
    walle.sadness(0.7)
    time.sleep(1)
    walle.sadness(0.3)

def happy(walle):
    walle.sadness(0)
    walle.blink()
    walle.sound("haha")
    time.sleep(2)
    walle.sadness(0.3)

def happy2(walle):
    walle.sound("whistle")
    walle.neckAngle(walle.get_coef("neck_angle")+0.1)
    walle.eyebrow(0.5)
    time.sleep(0.6)
    walle.neckAngle(walle.get_coef("neck_angle")-0.1)
    walle.eyebrow(0)
    time.sleep(0.7)
    a+=1

def happy3(walle):
    walle.headAngle(walle.get_coef("head_angle")+0.15)
    walle.manual("lid_R",1)
    time.sleep(0.3)
    walle.manual("lid_R",0)
    walle.headAngle(walle.get_coef("head_angle")-0.15)


def sadness(walle):
    walle.sadness(1)
    walle.lid(0.4)
    walle.manual("neck_L",0.2)
    walle.manual("neck_U",0)
    time.sleep(0.2)
    walle.sound(str(random.choice(['oh2', 'sight1'])))
    time.sleep(3.5)
    walle.neckAngle(walle.get_coef("neck_angle"))
    walle.sadness(0.3)
    walle.lid(0)

def rizz(walle):
    walle.sound('rizz')
    walle.lid(0.4)
    walle.eyebrow(1)
    time.sleep(0.2)
    walle.eyebrow(0)
    time.sleep(0.2)
    walle.eyebrow(1)
    time.sleep(0.2)
    walle.eyebrow(0)
    walle.lid(0)

def looking(walle):
    walle.neckLR(0)
    walle.neckAngle(0.2)
    walle.manual("shoulder_R",0.2)
    time.sleep(3)
    walle.manual("hand_R",0.2)
    time.sleep(0.5)
    walle.manual("hand_L",0.2)
    walle.neckLR(1)
    time.sleep(0.3)
    walle.blink()
    time.sleep(3)
    walle.manual("shoulder_R",0)
    walle.neckAngle(0.5)
    time.sleep(1)
    walle.neckLR(0)
    time.sleep(0.3)
    walle.blink()
    time.sleep(3)
    walle.neckLR(0.5)

def curious(walle):
    walle.eyebrow(1)
    walle.sadness(0)
    walle.headAngle(0)
    walle.sound("ah")
    time.sleep(1.5)
    walle.eyebrow(0)
    walle.sadness(0.2)
    walle.headAngle(0.5)

def surprise(walle):
    walle.eyebrow(1)
    walle.sadness(0)
    walle.sound(str(random.choices("waow1","waow2")))
    walle.arm(0.2)
    time.sleep(0.5)
    walle.arm(0)
    time.sleep(0.5)
    walle.eyebrow(0)
    walle.sadness(0.2)

def dance(walle):
    walle.neckAngle(0.5)
    walle.headAngle(0.5)
    time.sleep(0.5)
    walle.sound("sunday_clothe_cut")
    a=0
    while a<=4:
        walle.headAngle(0.3)
        walle.manual("shoulder_L", walle.get_coef("shoulder_L")+0.3)
        walle.manual("shoulder_R", walle.get_coef("shoulder_R")-0.3)
        time.sleep(0.9)
        walle.headAngle(0.7)
        walle.manual("shoulder_R", walle.get_coef("shoulder_R")+0.3)
        walle.manual("shoulder_L", walle.get_coef("shoulder_L")-0.3)
        time.sleep(0.9)
        a+=1
    walle.headAngle(0.5)
    walle.arm(walle.get_coef("shoulder_L"))
    walle.stop_sound()
    #coucou
    
def hello(walle):
    walle.manual("shoulder_L",0.7)
    walle.sound(str(random.choice(["walle1","walle2"])))
    time.sleep(0.8)
    walle.headAngle(0.8)
    time.sleep(0.5)
    walle.manual("hand_L", 0.3)
    time.sleep(0.5)
    walle.manual("hand_L", 0.6)
    time.sleep(0.5)
    walle.manual("hand_L", 0.3)
    time.sleep(0.5)
    walle.manual("hand_L", 0.5)
    time.sleep(0.5)
    walle.headAngle(0.5)
    walle.manual("shoulder_L",0)

EMOTES = {
    "Auto_adjust": auto_adjust,
    "Happy": happy,
    "Happy2": happy2,
    "Happy3": happy3,
    "Sadness": sadness,
    "Rizz": rizz,
    "Looking": looking,
    "Curious": curious,
    "Surprise": surprise,
    "Dance": dance,
    "Hello": hello
}

SMILE = {
    "Happy": happy,
    "Happy2": happy2,
    "Happy3": happy3,

}