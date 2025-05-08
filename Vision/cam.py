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
blink_threshold = 0.13
L_eye_history = [0]*5
R_eye_history = [0]*5

#body variables
last_results_pose = None
last_wrist_L = [0.0]*3
last_wrist_R = [0.0]*3
last_elbow_L = [0.0]*3
last_elbow_R = [0.0]*3
last_time = time.time()
velocity = [0]*4
surprised = False

def gen_frames():
    global last_frame, last_results,last_results_pose, last_time
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
            for landmark in results_pose.pose_landmarks.landmark:
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
    global last_frame, last_results, head_detected, blink, L_eye_closed, R_eye_closed, head_tilt_history, x_position_history, y_position_history, last_results_pose, last_wrist_L, last_wrist_R, last_elbow_L, last_elbow_R, last_time, velocity, surprised
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
        return None
    
    if last_results_pose.pose_landmarks:
        pose_landmarks = last_results_pose.pose_landmarks
        wrist_L = pose_landmarks.landmark[15]
        wrist_R = pose_landmarks.landmark[16]
        elbow_L = pose_landmarks.landmark[13]
        elbow_R = pose_landmarks.landmark[14]
        
        now= time.time()
        
        velocity[0] = np.sqrt((wrist_L.x - last_wrist_L[0])**2 + (wrist_L.y - last_wrist_L[1])**2 + (wrist_L.z - last_wrist_L[2])**2) / (now - last_time)
        velocity[1] = np.sqrt((wrist_R.x - last_wrist_R[0])**2 + (wrist_R.y - last_wrist_R[1])**2 + (wrist_R.z - last_wrist_R[2])**2) / (now - last_time)
        velocity[2] = np.sqrt((elbow_L.x - last_elbow_L[0])**2 + (elbow_L.y - last_elbow_L[1])**2 + (elbow_L.z - last_elbow_L[2])**2) / (now - last_time)
        velocity[3] = np.sqrt((elbow_R.x - last_elbow_R[0])**2 + (elbow_R.y - last_elbow_R[1])**2 + (elbow_R.z - last_elbow_R[2])**2) / (now - last_time)
        
        for i in velocity:
            if i > 0.008:
                surprised = True
                print(surprised)
            else:
                surprised = False

        # wrist position
        last_wrist_L = [wrist_L.x, wrist_L.y, wrist_L.z]
        last_wrist_R = [wrist_R.x, wrist_R.y, wrist_R.z]
        last_elbow_L = [elbow_L.x, elbow_L.y, elbow_L.z]
        last_elbow_R = [elbow_R.x, elbow_R.y, elbow_R.z]
    
def get_head_factor():
    if head_detected:
        global blink_threshold, L_eye_history, R_eye_history, velocity
        
        x_position= round(sum(x_position_history) / len(x_position_history),2)
        y_position= round(sum(y_position_history) / len(y_position_history),2)
        z_position= round(sum(z_position_history) / len(z_position_history),2)
        head_tilt = round(sum(head_tilt_history) / len(head_tilt_history),2)
        L_eye_ratio = round(sum(L_eye_history) / len(L_eye_history),2)
        R_eye_ratio = round(sum(R_eye_history) / len(R_eye_history),2)
        
        both_closed = (L_eye_ratio < blink_threshold) and (R_eye_ratio < blink_threshold)
        both_open = (L_eye_ratio >= blink_threshold) and (R_eye_ratio >= blink_threshold)
        left_closed = (L_eye_ratio < blink_threshold) and (R_eye_ratio >= blink_threshold)
        right_closed = (R_eye_ratio < blink_threshold) and (L_eye_ratio >= blink_threshold)
        
        blink_type = "none"
        if both_closed:
            blink_type = "blink"
        elif both_open:
            blink_type = "open"
        elif left_closed:
            blink_type = "wink_right"
        elif right_closed:
            blink_type = "wink_left"

        res = [x_position, y_position, z_position, head_tilt, blink_type ]
        
        print(velocity)
        
        return res
    else:
        return None