from mediapipe.tasks.python import vision
from mediapipe.tasks import python
import mediapipe as mp
import cv2

# === Callback ===
def gesture_callback(result, output_image, timestamp_ms):
    global gesture_label
    if result.gestures:
        gesture_label = result.gestures[0][0].category_name
    else:
        gesture_label = "Aucun geste"

gesture_label = "Chargement..."

# === Options ===
model_path = "gesture_recognizer.task"
BaseOptions = python.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=gesture_callback,
)

recognizer = GestureRecognizer.create_from_options(options)

# === Webcam ===
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    recognizer.recognize_async(mp_image, timestamp_ms)

    cv2.putText(frame, gesture_label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)
    cv2.imshow("Reconnaissance des gestes", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
