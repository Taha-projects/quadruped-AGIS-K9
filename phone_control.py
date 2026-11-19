import time
from threading import Lock, Thread

from adafruit_servokit import ServoKit
from flask import Flask, jsonify, render_template

# PCA9685: 0 FR hip, 1 FR knee, 2 FL hip, 3 FL knee,
#          4 BR hip, 5 BR knee, 6 BL hip, 7 BL knee
COUNT = 8
MIN_US, MAX_US = 600, 2400
HOME = [65, 110, 115, 90, 115, 90, 65, 90]
SIT = [65, 135, 115, 65, 115, 65, 65, 115]

HIP_BACK, HIP_FORWARD, KNEE_LIFT = 12, 28, 20
PHASE_SECONDS, UPDATE_SECONDS, ANGLE_STEP = 0.300, 0.015, 2
KNEE_SIGN = [-1, 1, -1, 1]  # FR, FL, BR, BL
HIP_SIGN = {
    "forward": [-1, 1, -1, 1],
    "backward": [1, -1, 1, -1],
    "left": [1, 1, 1, 1],
    "right": [-1, -1, -1, -1],
}
DANCE_A = [
    [8, 0, -8, 0, -8, 0, 8, 0],
    [0, 6, 0, -6, 0, -6, 0, 6],
    [-8, 0, 8, 0, 8, 0, -8, 0],
    [0, -6, 0, 6, 0, 6, 0, -6],
]
DANCE_B = [
    [8, 5, 0, 0, -8, -5, 0, 0],
    [0, 0, 8, 5, 0, 0, -8, -5],
    [-8, -5, 0, 0, 8, 5, 0, 0],
    [0, 0, -8, -5, 0, 0, 8, 5],
]

kit = ServoKit(channels=16, address=0x40, frequency=50)
for ch in range(COUNT):
    kit.servo[ch].set_pulse_width_range(MIN_US, MAX_US)

app = Flask(__name__)
lock = Lock()
mode = "pose"
pose_target = HOME.copy()
angles = HOME.copy()
phase = 0
phase_time = dance_time = wave_time = time.monotonic()
wave_angle = 70


def clamp(value):
    return max(0, min(180, int(value)))


def write(ch, angle):
    kit.servo[ch].angle = clamp(angle)


def move_toward(target):
    for ch in range(COUNT):
        if angles[ch] < target[ch]:
            angles[ch] = min(angles[ch] + ANGLE_STEP, target[ch])
        elif angles[ch] > target[ch]:
            angles[ch] = max(angles[ch] - ANGLE_STEP, target[ch])
        write(ch, angles[ch])


def gait_targets(direction, gait_phase):
    signs = HIP_SIGN[direction]
    target = HOME.copy()
    pair_a_moving = gait_phase in (0, 1)
    for leg in range(4):  # FR, FL, BR, BL
        pair_a = leg in (0, 3)
        moving = pair_a == pair_a_moving
        hip, knee = leg * 2, leg * 2 + 1
        if moving:
            forward_swing = gait_phase in (1, 3)
            offset = signs[leg] * HIP_FORWARD if forward_swing else -signs[leg] * HIP_BACK
            target[hip] = HOME[hip] + offset
            target[knee] = HOME[knee] + KNEE_SIGN[leg] * KNEE_LIFT
        else:
            target[hip] = HOME[hip] - signs[leg] * HIP_BACK
        target[hip] = clamp(target[hip])
        target[knee] = clamp(target[knee])
    return target


def animate():
    global phase, phase_time, wave_time, wave_angle
    while True:
        now = time.monotonic()
        with lock:
            if mode in HIP_SIGN:
                if now - phase_time >= PHASE_SECONDS:
                    phase = (phase + 1) % 4
                    phase_time = now
                move_toward(gait_targets(mode, phase))
            elif mode == "dance":
                elapsed = now - dance_time
                style = int(elapsed / 5.0) % 2
                pose = int(elapsed / 0.300) % 4
                table = DANCE_A if style == 0 else DANCE_B
                move_toward([clamp(HOME[ch] + table[pose][ch]) for ch in range(COUNT)])
            elif mode == "wave":
                target = HOME.copy()
                target[0], target[1] = wave_angle, 0
                move_toward(target)
                interval = 0.500 if wave_angle == 70 else 0.400
                if now - wave_time >= interval:
                    wave_angle = 65 if wave_angle in (70, 80) else 80
                    wave_time = now
            else:
                move_toward(pose_target)
        time.sleep(UPDATE_SECONDS)


@app.get("/")
def index():
    return render_template('index.html')


@app.post("/<action>")
def command(action):
    global mode, pose_target, phase, phase_time, dance_time, wave_time, wave_angle
    allowed = {"stand", "stop", "sit", "forward", "backward", "left", "right", "wave", "dance"}
    if action not in allowed:
        return jsonify(error="Unknown command"), 404
    with lock:
        if action in ("stand", "stop"):
            mode, pose_target = "pose", HOME.copy()
            message = "Returning to stand"
        elif action == "sit":
            mode, pose_target = "pose", SIT.copy()
            message = "Sitting"
        elif action in HIP_SIGN:
            mode, phase, phase_time = action, 0, time.monotonic()
            message = action.capitalize()
        elif action == "wave":
            mode, wave_angle, wave_time = "wave", 70, time.monotonic()
            message = "Waving"
        else:
            mode, dance_time = "dance", time.monotonic()
            message = "Dancing"
    return jsonify(message=message)


if __name__ == "__main__":
    with lock:
        for ch, angle in enumerate(HOME):
            write(ch, angle)
            time.sleep(0.100)
    Thread(target=animate, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)


