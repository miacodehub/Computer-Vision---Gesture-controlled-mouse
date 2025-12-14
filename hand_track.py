import cv2
import mediapipe as mp
import pyautogui
import math
import time

pyautogui.FAILSAFE = False

# -------------------
# Config
# -------------------
screen_w, screen_h = pyautogui.size()
PADDING = 0.25
SMOOTHING = 0.25

CLICK_THRESHOLD = 35
DRAG_THRESHOLD = 28
HOLD_THRESHOLD = 38
COOLDOWN = 0.5  # Increased for single click stability

RIGHT_CLICK_HOLD_TIME = 0.5
RIGHT_CLICK_COOLDOWN = 1.0
DOUBLE_CLICK_HOLD = 0.2

# -------------------
# State variables
# -------------------
smooth_x, smooth_y = 0, 0
left_drag_active = False
left_click_done = False
double_click_done = False
right_click_done = False
last_left_click = 0
last_double_click = 0
last_right_click_time = 0
double_click_start = 0
right_click_start = 0

# -------------------
# Mediapipe setup
# -------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cam = cv2.VideoCapture(0)

# -------------------
# Helper functions
# -------------------
def finger_up(lm, tip, pip):
    return lm[tip].y < lm[pip].y


def finger_bent(lm, tip, pip):
    return lm[tip].y > lm[pip].y

pinch_active = False

# -------------------
# Main loop
# -------------------
while True:
    ret, frame = cam.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            lm = handLms.landmark
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # -------------------
            # Cursor control
            # -------------------
            index_tip = lm[8]
            raw_x = index_tip.x
            raw_y = index_tip.y

            nx = (raw_x - PADDING) / (1 - 2 * PADDING)
            ny = (raw_y - PADDING) / (1 - 2 * PADDING)
            nx = max(0, min(1, nx))
            ny = max(0, min(1, ny))

            target_x = int(nx * screen_w)
            target_y = int(ny * screen_h)

            smooth_x = int(smooth_x * (1 - SMOOTHING) + target_x * SMOOTHING)
            smooth_y = int(smooth_y * (1 - SMOOTHING) + target_y * SMOOTHING)
            pyautogui.moveTo(smooth_x, smooth_y)

            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            cv2.circle(frame, (ix, iy), 10, (0, 255, 0), -1)

            # -------------------
            # Fingertips for gestures
            # -------------------
            thumb_x, thumb_y = int(lm[4].x * w), int(lm[4].y * h)
            middle_x, middle_y = int(lm[12].x * w), int(lm[12].y * h)

            dist_thumb_index = math.hypot(thumb_x - ix, thumb_y - iy)
            dist_thumb_middle = math.hypot(thumb_x - middle_x, thumb_y - middle_y)

            current_time = time.time()

            # -------------------
            # Left click (thumb + index pinch)
            # -------------------
            if dist_thumb_index < CLICK_THRESHOLD:
                if not pinch_active:
                    pyautogui.click()
                    pinch_active = True
                else:
                    pinch_active = False


            # -------------------
            # Drag (stateful)
            # -------------------
            if dist_thumb_index < DRAG_THRESHOLD:
                if not left_drag_active:
                    pyautogui.mouseDown()
                    left_drag_active = True
                    print("Drag START")
            elif left_drag_active and dist_thumb_index > HOLD_THRESHOLD:
                pyautogui.mouseUp()
                left_drag_active = False
                print("Drag END")

            # -------------------
            # Double click (thumb + middle)
            # -------------------
            if dist_thumb_middle < CLICK_THRESHOLD:
                if not double_click_done:
                    if double_click_start == 0:
                        double_click_start = current_time
                    elif current_time - double_click_start > DOUBLE_CLICK_HOLD:
                        pyautogui.doubleClick()
                        print("Double Click")
                        double_click_done = True
                        double_click_start = 0
            else:
                double_click_start = 0
                double_click_done = False

            # -------------------
            # Right click (index + middle bent, ring+pinky up)
            # -------------------
            index_bent = finger_bent(lm, 8, 6)
            middle_bent = finger_bent(lm, 12, 10)
            ring_up = finger_up(lm, 16, 14)
            pinky_up = finger_up(lm, 20, 18)

            right_click_gesture = index_bent and middle_bent and ring_up and pinky_up

            if right_click_gesture:
                if not right_click_done:
                    if right_click_start == 0:
                        right_click_start = current_time
                    elif current_time - right_click_start > RIGHT_CLICK_HOLD_TIME:
                        pyautogui.click(button='right')
                        print("Right Click")
                        right_click_done = True
                        right_click_start = 0
            else:
                right_click_start = 0
                right_click_done = False

    cv2.imshow("Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
