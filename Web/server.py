from flask import Flask, render_template, Response, request, redirect
from Vision.cam import gen_frames
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')


selected_mode = "Manual"
selected_emote = None
selected_servo = None
servo_position = 90
last_command = None
Shutdown = False

@app.route('/')
def index():
    return render_template('index.html', 
                           mode=selected_mode, 
                           emote=selected_emote, 
                           servo=selected_servo, 
                           position=servo_position)

@app.route('/set_mode', methods=["POST"])
def set_mode():
    global selected_mode
    selected_mode = request.form.get("mode")
    print(f"[Web] Mode reçu : {selected_mode}")
    return ('', 204)

@app.route('/set_emote', methods=["POST"])
def set_emote():
    global selected_emote
    selected_emote = request.form.get("emote")
    print(f"[Web] Emote reçue : {selected_emote}")
    return ('', 204)

@app.route('/set_servo', methods=["POST"])
def set_servo():
    global selected_servo, servo_position
    selected_servo = request.form.get("servo")
    servo_position = int(request.form.get("position"))
    print(f"[Web] Servo {selected_servo} à la position {servo_position}")
    return ('', 204)

@app.route('/send_command', methods=["POST"])
def send_command():
    global last_command
    last_command = request.form.get("command")
    if last_command == "shutdown":
        global Shutdown
        Shutdown = True
    print(f"[Web] Commande joystick reçue : {last_command}")
    return ('', 204)  # No content

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(selected_mode), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_selected_mode():
    return selected_mode

def get_last_command():
    global last_command
    temp = last_command
    last_command = None
    return temp

def get_shudown():
    return Shutdown

def get_selected_emote():
    global selected_emote
    temp = selected_emote
    selected_emote = None
    return temp

def get_servo_data():
    global selected_servo, servo_position
    temp1 = selected_servo
    temp2 = servo_position/180
    selected_servo = None
    servo_position = 90
    return temp1, temp2

def run_web_server():
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
