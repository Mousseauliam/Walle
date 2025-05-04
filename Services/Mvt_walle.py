from Services import Emotes
from Sounds.SoundPlayer import SoundPlayer
import serial
import time

class Walle:
    def __init__(self, port: str):
        self.serial_available = True
        try:
            self.serial = serial.Serial(port, baudrate=115200, timeout=1)
            print(f"[Mvt_Walle] ✅ Connexion au port {port} réussie.")
        except serial.SerialException as e:
            print(f"[Mvt_Walle] ❌ Erreur : Impossible d'ouvrir le port {port}.")
            self.serial_available = False
            
        self.coef_init = {
            "lid_L":1.0,
            "lid_R":1.0,
            "eyebrow_L": 0.0,
            "eyebrow_R": 0.0,
            "UD_L": 0.55,
            "UD_R": 0.6,
            "head_angle": 0.5,
            "eye_sad": 0.0,
            "neck_U":0.0,
            "neck_L":0.0,
            "neck_LR":0.0,
            "neck_level":1.0,
            "neck_angle":0.0,
            "arm_L":0.5,
            "arm_R":0.5,
            "hand_L":1.0,
            "hand_R":1.0,
            "speed_L":0.5,
            "speed_R":0.5
        }
        self.coef = self.coef_init.copy()
        #self.update(self.coef.keys())
        
        self.sound = SoundPlayer()
        

    def update(self, tab):
        res = ""
        for key in tab:
            res += f"{key}%{self.coef[key]}\n"
            #print(f"[Mvt_Walle] 🔄 {key} = {self.coef[key]}")

        if self.serial_available:
            self.serial.write(res.encode())
            print("[Mvt_Walle] ➡️ Envoyé à l'Arduino\n")
        else:
            print("[Mvt_Walle] Erreur envoie arduino\n")

    def blink(self):
        self.coef['lid_L']=0
        self.coef['lid_R']=0
        self.update(['lid_L','lid_R'])
        print("[Mvt_Walle] WALL-E cligne des yeux. 1")
        time.sleep(0.15)
        self.coef['lid_L']=1
        self.coef['lid_R']=1
        self.update(['lid_L','lid_R'])
        
    def manual(self,name,angle):
        self.coef[name]=angle
        print(f"[Mvt_Walle] {name} réglé à {angle}")
        self.update([name])

    def headAngle(self, angle=None):
        if angle is None:
            angle = self.coef["head_angle"]
        else:
            self.coef["head_angle"] = angle

        base_position = 0.5

        UD_L_temp = base_position - (0.5-angle)
        UD_R_temp = base_position + (0.5-angle)

        # sadness effect
        self.coef["UD_L"] = max(0, min(1,((1 - self.coef["eye_sad"]) * UD_L_temp)))
        self.coef["UD_R"] = max(0, min(1,((1 - self.coef["eye_sad"]) * UD_R_temp)))

        self.update(["UD_L", "UD_R"])
        
    def neckLR(self, angle):
        self.coef["neck_LR"]=angle
        print(f"[Mvt_Walle] WALL-E tourne la tête de {angle}")
        self.update(["neck_LR"])

    def eyebrow(self, angle):
        self.coef["eyebrow_L"] = angle
        self.coef["eyebrow_R"] = angle
        self.update(["eyebrow_L", "eyebrow_R"])

    def sadness(self, angle):
        self.coef["eye_sad"] = angle
        print(f"[Mvt_Walle] Niveau de tristesse réglé à {angle}")
        self.headAngle()
        
        
    def neckLevel(self, necklevel=None):
        neckAngle = self.coef["neck_angle"]

        if necklevel is None:
            necklevel = self.coef["neck_level"]
        else:
            self.coef["neck_level"] = necklevel

        neck_L_temp = (1 - neckAngle) * necklevel
        neck_U_temp = neckAngle * necklevel

        self.coef["neck_L"] = max(0, min(1, neck_L_temp))
        self.coef["neck_U"] = max(0, min(1, neck_U_temp))
        
        print(f"[Mvt_Walle] Neck_level réglé à {necklevel}")
        self.update(["neck_L", "neck_U"])
        
    def neckAngle(self, neckAngle):
        self.coef["neck_angle"] = neckAngle
        print(f"[Mvt_Walle] Neck_angle réglé à {neckAngle}")
        self.neckLevel()
        
    def forward(self, speed=0.5):
        self.coef["speed_L"] = speed
        self.coef["speed_R"] = speed
        print(f"[Mvt_Walle] WALL-E avance à la vitesse {speed}")
        self.update(["speed_L", "speed_R"])
        
    def backward(self, speed=0.5):
        self.coef["speed_L"] = -speed
        self.coef["speed_R"] = -speed
        print(f"[Mvt_Walle] WALL-E recule à la vitesse {speed}")
        self.update(["speed_L", "speed_R"])
        
    def turn (self, speed=0.5):
        self.coef["speed_L"] = (0.5-speed)*2
        self.coef["speed_R"] = (0.5-speed)*-2
        print(f"[Mvt_Walle] WALL-E tourne à la vitesse {(0.5-speed)*2}")
        self.update(["speed_L", "speed_R"])
        
    def emote(self, name):
        if name in Emotes.EMOTES:
            Emotes.EMOTES[name](self)
        
    def sound(self, name):
        if not self.sound.is_playing():
            self.sound.play(name)
            
    def get_coef(self, name):
        if name in self.coef:
            return self.coef[name]
        else:
            print(f"[Mvt_Walle] Erreur: {name} n'est pas un coefficient valide.")
            return None

    def sleep(self):
        self.coef = self.coef_init.copy()
        self.update(self.coef.keys())
        

    def close(self):
        if self.serial_available:
            self.serial.close()
        print("[Mvt_Walle] Port série fermé.")
