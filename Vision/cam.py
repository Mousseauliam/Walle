import time
import cv2
from picamera2 import Picamera2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
pose = mp_pose.Pose(static_image_mode=False)

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
y_position_history = [0]*4
z_position_history = [0]*5
head_detected = False

#eyes variables
blink_threshold = 0.14
L_eye_history = [0]*5
R_eye_history = [0]*5

#body variables
last_results_pose = None
last_wrist_L = [[0.0, 0.0, 0.0] for _ in range(10)]
last_wrist_R = [[0.0, 0.0, 0.0] for _ in range(10)]
last_elbow_L = [[0.0, 0.0, 0.0] for _ in range(10)]
last_elbow_R = [[0.0, 0.0, 0.0] for _ in range(10)]
last_process = time.time()
velocity = [0]*12
emote = None
last_emote = 0
surprise_threshold = 5
hello_threshold = 1
above_head = False

def gen_frames():
    global last_frame, last_results,last_results_pose, last_process
    while True:
        frame = picam2.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        results = face_mesh.process(frame)
        results_pose = pose.process(frame)
        
        last_frame = frame
        last_results = results
        last_results_pose = results_pose
        h, w, _ = frame.shape
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        
        if results_pose.pose_landmarks:
            key_landmarks = [
                mp_pose.PoseLandmark.LEFT_WRIST,
                mp_pose.PoseLandmark.RIGHT_WRIST,
                mp_pose.PoseLandmark.LEFT_ELBOW,
                mp_pose.PoseLandmark.RIGHT_ELBOW
            ]
            for landmark_id in key_landmarks:
                landmark = results_pose.pose_landmarks.landmark[landmark_id.value]
                x, y = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)
                
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        frame_process()
        time.sleep(0.03)

def frame_process():
    head_factor()
    body_factor()
    
def head_factor():
    global head_detected, last_results, x_position_history, y_position_history, z_position_history, head_tilt_history, L_eye_history, R_eye_history
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
        z_position_history.pop(0)
        z_position_history.append(nose_tip.z)
        

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
        
def body_factor():
    global last_results_pose, last_wrist_L, last_wrist_R, last_elbow_L, last_elbow_R, last_process, velocity, above_head
    if last_results_pose.pose_landmarks:
        pose_landmarks = last_results_pose.pose_landmarks
        wrist_L = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
        wrist_R = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        elbow_L = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        elbow_R = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        
        now= time.time()
        
        velocity = velocity[4:]
        velocity.append(np.sqrt((wrist_L.x - last_wrist_L[9][0])**2 + (wrist_L.y - last_wrist_L[9][1])**2 + (wrist_L.z - last_wrist_L[9][2])**2) / (now - last_process))
        velocity.append(np.sqrt((wrist_R.x - last_wrist_R[9][0])**2 + (wrist_R.y - last_wrist_R[9][1])**2 + (wrist_R.z - last_wrist_R[9][2])**2) / (now - last_process))
        velocity.append(np.sqrt((elbow_L.x - last_elbow_L[9][0])**2 + (elbow_L.y - last_elbow_L[9][1])**2 + (elbow_L.z - last_elbow_L[9][2])**2) / (now - last_process))
        velocity.append(np.sqrt((elbow_R.x - last_elbow_R[9][0])**2 + (elbow_R.y - last_elbow_R[9][1])**2 + (elbow_R.z - last_elbow_R[9][2])**2) / (now - last_process))
        
        h_wrist = nose_tip.y + 0.15
        h_elbow = nose_tip.y +0.35
        above_head = ((last_elbow_L[9][1]< h_elbow) and (last_wrist_L[9][1]< h_wrist)) or ((last_elbow_R[9][1]< h_elbow) and (last_wrist_R[9][1]< h_wrist))
        
        last_process = time.time()
        
        # wrist position
        last_wrist_L.pop(0)
        last_wrist_L.append([wrist_L.x, wrist_L.y, wrist_L.z])
        last_wrist_R.pop(0)
        last_wrist_R.append([wrist_R.x, wrist_R.y, wrist_R.z])
        last_elbow_L.pop(0)
        last_elbow_L.append([elbow_L.x, elbow_L.y, elbow_L.z])
        last_elbow_R.pop(0)
        last_elbow_R.append([elbow_R.x, elbow_R.y, elbow_R.z])

def is_waving(history, threshold=0.02, min_crossings=2):
    crossings = 0
    for i in range(2, len(history)):
        if (history[i-2] - history[i-1]) * (history[i-1] - history[i]) < 0:
            if abs(history[i-1] - history[i]) > threshold:
                crossings += 1
    return crossings >= min_crossings

def get_head_factor():
    if head_detected:
        global blink_threshold, L_eye_history, R_eye_history, emote, surprise_threshold, hello_threshold, last_emote, above_head, last_wrist_L, last_wrist_R, velocity
        
        x_position= round(sum(x_position_history) / len(x_position_history),2)
        y_position= round(sum(y_position_history) / len(y_position_history),2)
        z_position= round(sum(z_position_history) / len(z_position_history),2)
        head_tilt = round(sum(head_tilt_history) / len(head_tilt_history),2)
        L_eye_ratio = round(sum(L_eye_history) / len(L_eye_history),2)
        R_eye_ratio = round(sum(R_eye_history) / len(R_eye_history),2)
        
        both_closed = (L_eye_ratio < blink_threshold) and (R_eye_ratio < blink_threshold)
        both_open = (L_eye_ratio >= blink_threshold) and (R_eye_ratio >= blink_threshold)
        left_closed = (L_eye_ratio < blink_threshold) and (R_eye_ratio >= blink_threshold)
        right_closed = (R_eye_ratio < (blink_threshold+0.02)) and (L_eye_ratio >= blink_threshold)
        
        blink_type = "none"
        if both_closed:
            blink_type = "blink"
        elif both_open:
            blink_type = "open"
        elif left_closed:
            blink_type = "wink_right"
        elif right_closed:
            blink_type = "wink_left"
    if (time.time() - last_emote) > 4:
        velocity_moy = []
        for i in range(2):
            velocity_moy.append((velocity[i] + velocity[i+2] + velocity[i+4] + velocity[i+6] + velocity[i+8] + velocity[i+10] )/6)
        
        print(velocity_moy, is_waving([w[0] for w in last_wrist_L]) , is_waving([w[0] for w in last_wrist_R]), above_head)
        
        if (is_waving([w[0] for w in last_wrist_L]) or is_waving([w[0] for w in last_wrist_R])) and above_head:
            emote = "Hello"
            print("Hello")
            last_emote = time.time()
        elif any(velocity > surprise_threshold for velocity in velocity_moy):
            emote = "Surprise"
            print("Surprise")
            last_emote = time.time()
        else:
            emote = None

    res = [x_position, y_position, z_position, head_tilt, blink_type, emote]
    emote=None    
    return res
    