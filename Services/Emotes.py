import time

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
    walle.sadness(0)

def happy(walle):
    walle.sadness(0)
    walle.eyebrow(1)
    walle.blink()
    #Mettre un son joyeux

def sadness(walle):
    walle.sadness(1)
    walle.eyebrow(1)
    walle.lid(0.4)
    #walle.neck_level(0)
    #Mettre un son triste

def rizz(walle):
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
    #walle.armR(0.4)
    time.sleep(3)
    walle.handR(1)
    time.sleep(0.5)
    walle.handR(0)
    walle.neckLR(1)
    time.sleep(0.3)
    walle.blink()
    time.sleep(3)
    #walle.armR(0)
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
    #Mettre le son "Wow!"
    time.sleep(1.5)
    walle.eyebrow(0)
    walle.sadness(0.2)
    walle.headAngle(0.5)

def surprise(walle):
    walle.eyebrow(1)
    walle.sadness(0)
    #walle.arm(0.3)
    time.sleep(0.5)
    #walle.arm(0)
    time.sleep(1)
    walle.eyebrow(0)
    walle.sadness(0.2)


EMOTES = {
    "Auto_adjust": auto_adjust,
    "Happy": happy,
    "Sadness": sadness,
    "Rizz": rizz,
    "Looking": looking,
    "Curious": curious,
    "Surprise": surprise
}