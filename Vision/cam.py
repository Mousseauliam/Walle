import time
import cv2
from picamera2 import Picamera2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Camera init
screen_width, screen_height = 1240, 960
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(
main={"format": "RGB888", "size": (screen_width, screen_height)})
picam2.configure(preview_config)
picam2.start()

#globale variables
last_frame = None
last_results = None
head_tilt_history=[0]*10
x_position_history = [0]*5
y_position_history = [0]*5
head_detected = False

blink_threshold = 0.14
last_blink = 0
L_eye_history = [0]*5
R_eye_history = [0]*5

def gen_frames():
    global last_frame, last_results
    while True:
        frame = picam2.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        results = face_mesh.process(frame)
        last_frame = frame
        last_results = results
        h, w, _ = frame.shape
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        frame_process()
        time.sleep(0.03)


def frame_process():
    global last_frame, last_results, head_detected, blink, L_eye_closed, R_eye_closed, head_tilt_history, x_position_history, y_position_history
    if last_results.multi_face_landmarks:
        head_detected = True
        face_landmarks = last_results.multi_face_landmarks[0]
        L_eye_bottom = face_landmarks.landmark[145] 
        R_eye_bottom = face_landmarks.landmark[374] 
        nose_tip = face_landmarks.landmark[1]
        
        L_eye_top = face_landmarks.landmark[159]  # Haut de l'œil gauche
        R_eye_top = face_landmarks.landmark[386]  # Haut de l'œil droit
        L_eye_L = face_landmarks.landmark[130]  # Coin gauche œil gauche
        L_eye_R = face_landmarks.landmark[133]  # Coin droit œil gauche
        R_eye_L = face_landmarks.landmark[362]  # Coin gauche œil droit
        R_eye_R = face_landmarks.landmark[263]  # Coin droit œil droit  

        # position
        x_position_history.pop(0)
        x_position_history.append(nose_tip.x)
        y_position_history.pop(0)
        y_position_history.append(nose_tip.y)

        # head angle
        dx = R_eye_bottom.x - L_eye_bottom.x
        dy = R_eye_bottom.y - L_eye_bottom.y
        angle = np.arctan2(dy, dx)
        head_tilt_history.pop(0)
        head_tilt_history.append((angle / (np.pi / 4) + 1) / 2)
        
        #blink detection
        L_eye_history.pop(0)
        L_eye_history.append(abs(L_eye_top.y - L_eye_bottom.y)/abs(L_eye_L.x-L_eye_R.x))
        R_eye_history.pop(0)
        R_eye_history.append(abs(R_eye_top.y - R_eye_bottom.y)/abs(R_eye_L.x-R_eye_R.x))
        
            
    else:
        head_detected = False
        return None
    
def get_head_factor():
    if head_detected:
        global blink_threshold, L_eye_history, R_eye_history, last_blink
        
        x_position= round(sum(x_position_history) / len(x_position_history),2)
        y_position= round(sum(y_position_history) / len(y_position_history),2)
        head_tilt = round(sum(head_tilt_history) / len(head_tilt_history),2)
        L_eye_ratio = round(sum(L_eye_history) / len(L_eye_history),2)
        R_eye_ratio = round(sum(R_eye_history) / len(R_eye_history),2)
        
        both_closed = (L_eye_ratio < blink_threshold) and (R_eye_ratio < blink_threshold)
        both_open = (L_eye_ratio >= blink_threshold) and (R_eye_ratio >= blink_threshold)
        left_closed = (L_eye_ratio < blink_threshold) and (R_eye_ratio >= blink_threshold)
        right_closed = (R_eye_ratio < blink_threshold) and (L_eye_ratio >= blink_threshold)
        
        blink_type = "none"
        if both_closed and (time.time() - last_blink > 1.5):
            blink_type = "blink"
        elif both_open:
            blink_type = "open"
        elif left_closed:
            blink_type = "wink_left"
        elif right_closed:
            blink_type = "wink_right"
        last_blink = time.time()

        res = [x_position, y_position, head_tilt, blink_type ]
        blink = False
        return res
    else:
        return None