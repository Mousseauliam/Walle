from Services import Emotes
from Sounds.SoundPlayer import SoundPlayer
import serial
import time

class Walle:
    def __init__(self, port: str):
        self.sound_player = SoundPlayer()
        
        self.serial_available = True
        try:
            self.serial = serial.Serial(port, baudrate=115200, timeout=1)
            print(f"[Mvt_Walle] ✅ Connexion au port {port} réussie.")
        except serial.SerialException as e:
            print(f"[Mvt_Walle] ❌ Erreur : Impossible d'ouvrir le port {port}.")
            self.serial_available = False
            
        self.coef_init = {
            "lid_L":1,
            "lid_R":1,
            "eyebrow_L": 0.1,
            "eyebrow_R": 0.1,
            "UD_L": 0,
            "UD_R": 0,
            "neck_U":0,
            "neck_L":0,
            "neck_LR":0.5,
            "shoulder_L":0.5,
            "shoulder_R":0.5,
            "hand_L":0.5,
            "hand_R":0.5,
            "speed_L":0.5,
            "speed_R":0.5,
            "head_angle": 0.5,
            "neck_level":1.0,
            "neck_angle":0.4,
            "sadness": 0.3,
        }
        
        self.coef = self.coef_init.copy()
        
        
        time.sleep(2)
        self.sound("start1")
        self.wake_up()
        
        
        
        

    def update(self, tab):
        res = ""
        for key in tab:
            res += f"{key}%{self.coef[key]}\n"
            print(f"[Mvt_Walle] 🔄 {key} = {self.coef[key]}")

        if self.serial_available:
            self.serial.write(res.encode())
            print("[Mvt_Walle] ➡️ Envoyé à l'Arduino\n")
        else:
            print("[Mvt_Walle] Erreur envoie arduino\n")

    def blink(self):
        self.coef['lid_L']=1
        self.coef['lid_R']=1
        self.update(['lid_L','lid_R'])
        print("[Mvt_Walle] WALL-E cligne des yeux. 1")
        time.sleep(0.15)
        self.coef['lid_L']=0
        self.coef['lid_R']=0
        self.update(['lid_L','lid_R'])
        
    def manual(self,name,angle):
        if (self.coef[name] != angle) :
            self.coef[name]=round(max(0,min(1,angle)),2)
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
        self.coef["UD_L"] = round(max(0, min(1,((1 - self.coef["sadness"]) * UD_L_temp))), 2)
        self.coef["UD_R"] = round(max(0, min(1,((1 - self.coef["sadness"]) * UD_R_temp))), 2)

        self.update(["UD_L", "UD_R"])
        
    def neckLR(self, angle):
        self.coef["neck_LR"]=angle
        print(f"[Mvt_Walle] WALL-E tourne la tête de {angle}")
        self.update(["neck_LR"])

    def eyebrow(self, angle):
        self.coef["eyebrow_L"] = angle
        self.coef["eyebrow_R"] = angle
        self.update(["eyebrow_L", "eyebrow_R"])
    
    def lid(self, angle):
        self.coef["lid_L"] = angle
        self.coef["lid_R"] = angle
        self.update(["lid_L", "lid_R"])

    def sadness(self, angle):
        self.coef["sadness"] = angle
        print(f"[Mvt_Walle] Niveau de tristesse réglé à {angle}")
        self.headAngle()
        
    def hand(self, angle):
        self.coef["hand_L"] = angle
        self.coef["hand_R"] = angle
        self.update(["hand_L", "hand_R"])

    def arm(self, angle):
        self.coef["shoulder_L"] = angle
        self.coef["shoulder_R"] = angle
        self.update(["shoulder_L", "shoulder_R"])

    """  
    def neckLevel(self, necklevel=None):
        neckAngle = self.coef["neck_angle"]

        if necklevel is None:
            necklevel = self.coef["neck_level"]
        else:
            self.coef["neck_level"] = necklevel


        if neckAngle == 0:
            neck_L = 1
            neck_U = 0
        elif neckAngle == 1:
            neck_L = 0
            neck_U = 1
        elif neckAngle == 0.5:
            neck_L = necklevel
            neck_U = necklevel
        else:

            neck_L = (1 - neckAngle) if neckAngle < 0.5 else 0
            neck_U = neckAngle if neckAngle > 0.5 else 0


        self.coef["neck_L"] = max(0, min(1, neck_L))
        self.coef["neck_U"] = max(0, min(1, neck_U))

        print(f"[Mvt_Walle] Neck_level réglé à {necklevel}")
        self.update(["neck_L", "neck_U"])
        """
    def neckAngle(self, neckAngle):
        self.coef["neck_angle"] = neckAngle
        self.coef["neck_L"]= (1-neckAngle)
        self.coef["neck_U"]= neckAngle
        print(f"[Mvt_Walle] Neck_angle réglé à {neckAngle}")
        self.update(["neck_L", "neck_U"])

  def neck_levelbis(self, neckLevel):
    neck_L = walle.get_coef["neck_L"]
    neck_U = walle.get_coef["neck_U"]

    if 0 <= neckLevel < 0.5:
        delta = neckLevel
        # Réduction
        new_neck_L = neck_L - delta
        new_neck_U = neck_U - delta
        # Gestion des bornes
        if new_neck_L < 0 and new_neck_U < 0:
            new_neck_L, new_neck_U = 0.0, 0.0
        elif new_neck_L < 0:
            reste = -new_neck_L  # quantité qu'on n'a pas pu retirer à L
            new_neck_L = 0.0
            new_neck_U = max(0.0, new_neck_U - reste)
        elif new_neck_U < 0:
            reste = -new_neck_U
            new_neck_U = 0.0
            new_neck_L = max(0.0, new_neck_L - reste)
        # sinon, tout va bien

    elif neckLevel == 0.5:
        new_neck_L = 0.5
        new_neck_U = 0.5

    elif 0.5 < neckLevel <= 1.0:
        delta = neckLevel - 0.5
        new_neck_L = neck_L + delta
        new_neck_U = neck_U + delta
        # Gestion des bornes supérieures
        if new_neck_L > 1 and new_neck_U > 1:
            new_neck_L, new_neck_U = 1.0, 1.0
        elif new_neck_L > 1:
            reste = new_neck_L - 1  # quantité en excès sur L
            new_neck_L = 1.0
            new_neck_U = min(1.0, new_neck_U + reste)
        elif new_neck_U > 1:
            reste = new_neck_U - 1
            new_neck_U = 1.0
            new_neck_L = min(1.0, new_neck_L + reste)
        # sinon, tout va bien

    else:
        raise ValueError("neckLevel doit être dans [0, 1]")

    self.coef["neck_L"] = new_neck_L
    self.coef["neck_U"] = new_neck_U
    self.update(["neck_L", "neck_U"])

    def move(self, speed=0.5):
        self.coef["speed_L"] = speed
        self.coef["speed_R"] = speed
        print(f"[Mvt_Walle] WALL-E avance à la vitesse {speed}")
        self.update(["speed_L","speed_R"])
        
    def turn (self, angle=0.5):
        if (angle<0.5):
            side='speed_L'
        elif (angle>0.5):
            side='speed_R'
        else:
            return
        speed=self.coef[side]
        self.coef[side]=(speed -0.2) if speed>0.5 else (speed +0.2)
        print(f"[Mvt_Walle] WALL-E tourne à la vitesse {side}")
        self.update([side])
        time.sleep(abs(angle-0.5)*5)
        self.coef[side]=speed
        self.update([side])
        
    def emote(self, name):
        if name in Emotes.EMOTES:
            Emotes.EMOTES[name](self)
             
    def sound(self, name):
        if not self.sound_player.is_playing():
            self.sound_player.play(name)
            
    def stop_sound(self):
        if self.sound_player.is_playing():
            self.sound_player.stop()

    def get_coef(self, name):
        if name in self.coef:
            return self.coef[name]
        else:
            print(f"[Mvt_Walle] Erreur: {name} n'est pas un coefficient valide.")
            return None

    def sleep(self):
        self.manual("lid_L", 1)
        self.manual("lid_R", 1)
        self.manual("eyebrow_L", 0.0)
        self.manual("eyebrow_R", 0.0)
        self.manual("UD_L", 0)
        self.manual("UD_R", 0)
        self.manual("neck_U", 0.0)
        self.manual("neck_L", 0)
        self.manual("neck_LR", 0.5)
        self.manual("shoulder_L", 0)
        self.manual("shoulder_R", 0)
        self.manual("hand_L", 0.5)
        self.manual("hand_R", 0.5)
        
    def wake_up(self):
        self.manual("lid_L", 0)
        self.manual("lid_R", 0)
        time.sleep(0.3)
        self.manual("eyebrow_L", 0.0)
        self.manual("eyebrow_R", 0.0)
        time.sleep(0.3)
        self.neckAngle(0.5)
        time.sleep(0.3)
        self.neckAngle(0.4)
        self.manual("neck_LR", 0.5)
        time.sleep(1)
        self.manual("shoulder_L", 0.05)
        self.manual("shoulder_R", 0.1)
        time.sleep(0.5)
        self.manual("hand_L", 0.5)
        self.manual("hand_R", 0.5)
        self.sadness(0.3)
        time.sleep(1)
        self.emote("Auto_adjust")
        

    def close(self):
        if self.serial_available:
            self.serial.close()
        print("[Mvt_Walle] Port série fermé.")
