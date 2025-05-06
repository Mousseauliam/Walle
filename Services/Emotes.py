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

def angry(walle):
    walle.sadness(0.5)
    walle.eyebrow(1)
    walle.lid(0.5)

EMOTES = {
    "Auto_adjust": auto_adjust,
    "Happy": happy,
    "Angry": angry
}