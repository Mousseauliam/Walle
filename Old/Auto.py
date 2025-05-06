import cv2
import mediapipe as mp
import numpy as np
import time

# Initialisation de MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Capture vidéo
cap = cv2.VideoCapture(0)

# Initialisation des FPS
pTime = time.time()
fps = 0

# blink
BLINK_THRESHOLD = 0.12
L_blink_count = 0
R_blink_count = 0
L_eye_closed = False
R_eye_closed = False

#general
head_tilt_history=[0]*20

while cap.isOpened():
    check, frame = cap.read()
    if not check:
        break

    # Convertir en RGB pour MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    h, w, _ = frame.shape  # Dimensions de l'image

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Points clés des yeux
            L_eye_top = face_landmarks.landmark[159]  # Haut de l'œil gauche
            L_eye_bottom = face_landmarks.landmark[145]  # Bas de l'œil gauche
            R_eye_top = face_landmarks.landmark[386]  # Haut de l'œil droit
            R_eye_bottom = face_landmarks.landmark[374]  # Bas de l'œil droit
            L_eye_L = face_landmarks.landmark[130]  # Coin gauche œil gauche
            L_eye_R = face_landmarks.landmark[133]  # Coin droit œil gauche
            R_eye_L = face_landmarks.landmark[362]  # Coin gauche œil droit
            R_eye_R = face_landmarks.landmark[263]  # Coin droit œil droit
            nose_tip = face_landmarks.landmark[1]  # Pointe du nez

            # Position X et Y normalisées 
            x_position = (nose_tip.x - 0.5) * 2
            y_position = (nose_tip.y - 0.5) * -2

            # Inclinaison de la tete
            dx = R_eye_bottom.x - L_eye_bottom.x
            dy = R_eye_bottom.y - L_eye_bottom.y
            angle = np.arctan2(dy, dx)
            head_tilt_history.pop(0)
            head_tilt_history.append(np.clip(angle / (np.pi / 4), -1, 1))
            
            # Distance verticale normalisée pour chaque œil
            L_eye_ratio = abs(L_eye_top.y - L_eye_bottom.y)/abs(L_eye_L.x-L_eye_R.x)
            R_eye_ratio = abs(R_eye_top.y - R_eye_bottom.y)/abs(R_eye_L.x-R_eye_R.x)

            # Détection clignement œil gauche
            if L_eye_ratio < BLINK_THRESHOLD:
                if not L_eye_closed:
                    L_blink_count += 1
                    L_eye_closed = True
            else:
                L_eye_closed = False

            # Détection clignement œil droit
            if R_eye_ratio < BLINK_THRESHOLD:
                if not R_eye_closed:
                    R_blink_count += 1
                    R_eye_closed = True
            else:
                R_eye_closed = False
            print(f"Clignements gauche: {L_blink_count}, Clignements droit: {R_blink_count}")
            """
            # Affichage des compteurs de clignement
            cv2.putText(frame, f"Clignements gauche: {L_blink_count}", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, f"Clignements droit: {R_blink_count}", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            """
            # Affichage des points clés (optionnel)
            for landmark in [L_eye_top, L_eye_bottom, R_eye_top, R_eye_bottom]:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (cx, cy), 3, (0, 255, 255), -1)

    # Calcul des FPS
    fps += 1
    cTime = time.time()
    if cTime - pTime >= 1:  # Mise à jour chaque seconde
        #print(fps)
        fps = 0
        pTime = cTime
    
    head_tilt_display=sum(head_tilt_history)/len(head_tilt_history)
    cv2.putText(frame, f"headTilt: {head_tilt_display:.3f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, f"Z: {nose_tip.z:.3f}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)    
    
    # Afficher la vidéo
    cv2.imshow('Face Tracking', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Appuyer sur Échap pour quitter
        break

cap.release()
cv2.destroyAllWindows()
