import cv2
import numpy as np
import face_recognition
import os
import sys
import dlib
from scipy.spatial import distance as dist
from imutils import face_utils
from datetime import datetime
import pandas as pd

import database

ENCODINGS_FILE = "encodings.npz"
ATTENDANCE_FILE = "attendance.xlsx"
WINDOW = "Smart Attendance"

DISPLAY_W = 1280        # every frame is resized to this width before processing / display
SCALE = 0.25            # faces are detected on a 25% copy of the frame for speed
RECOGNISE_EVERY = 5     # the face encoder (slowest step) runs once every N frames
TOLERANCE = 0.6         # max face distance to count as a match

blink_thresh = 0.5
succ_frame = 2

FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE, GREEN, AMBER, RED = (255, 255, 255), (80, 200, 60), (0, 190, 255), (60, 60, 230)


# ---------- Load known faces (created by encode_faces.py) ----------

if not os.path.exists(ENCODINGS_FILE):
    print(f"{ENCODINGS_FILE} not found. Run 'python encode_faces.py' first.")
    sys.exit(1)

data = np.load(ENCODINGS_FILE)
className = [str(n) for n in data["names"]]
encodedimages = data["encodings"]
print(f"Loaded {len(className)} known faces: {className}")

students = database.get_all_students()
print(f"Loaded {len(students)} students from {database.DB_FILE}")


# ---------- Attendance ----------

def read_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        try:
            return pd.read_excel(ATTENDANCE_FILE, engine='openpyxl')
        except Exception:
            print("Corrupted file detected, creating a new Excel file.")
    return pd.DataFrame(columns=['Name', 'Date', 'Time'])


def load_marked_today():
    """{name: time} for everyone already marked today, so they aren't asked to blink again."""
    df = read_attendance()
    today = datetime.now().strftime('%Y-%m-%d')
    df = df[df['Date'].astype(str).str[:10] == today]
    return dict(zip(df['Name'], df['Time']))


def attendace(name):
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    df = read_attendance()
    already_marked = ((df['Name'] == name) & (df['Date'].astype(str).str[:10] == date_str)).any()

    if not already_marked:
        new_entry = pd.DataFrame([[name, date_str, time_str]], columns=['Name', 'Date', 'Time'])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(ATTENDANCE_FILE, index=False, engine='openpyxl')
    return time_str


# ---------- Recognition + blink helpers ----------

def identify(encoding):
    """Return the matched name (upper-case) or None for an unknown face."""
    if len(encodedimages) == 0:
        return None
    facedis = face_recognition.face_distance(encodedimages, encoding)
    matchIndex = np.argmin(facedis)
    if facedis[matchIndex] <= TOLERANCE:
        return className[matchIndex].upper()
    return None


def calculate_EAR(eye):
    y1 = dist.euclidean(eye[1], eye[5])
    y2 = dist.euclidean(eye[2], eye[4])
    x1 = dist.euclidean(eye[0], eye[3])
    return (y1 + y2) / x1


# ---------- Drawing helpers ----------

def put(img, text, org, scale=0.55, color=WHITE, thick=1):
    cv2.putText(img, text, org, FONT, scale, color, thick, cv2.LINE_AA)


def shade(img, x1, y1, x2, y2, alpha=0.6):
    """Darken a rectangle so text on top stays readable."""
    h, w = img.shape[:2]
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
    if x2 > x1 and y2 > y1:
        roi = img[y1:y2, x1:x2]
        img[y1:y2, x1:x2] = cv2.addWeighted(roi, 1 - alpha, np.zeros_like(roi), alpha, 0)


def draw_info_card(img, box, lines, color):
    """Small panel with student details beside the face box."""
    x1, y1, x2, y2 = box
    card_w, line_h, pad = 250, 24, 10
    card_h = pad * 2 + line_h * len(lines)
    cx = x2 + 12 if x2 + 12 + card_w < img.shape[1] else max(0, x1 - 12 - card_w)
    cy = min(max(0, y1), img.shape[0] - card_h)
    shade(img, cx, cy, cx + card_w, cy + card_h, alpha=0.65)
    cv2.rectangle(img, (cx, cy), (cx + card_w, cy + card_h), color, 1)
    for i, text in enumerate(lines):
        put(img, text, (cx + pad, cy + pad + 17 + i * line_h), 0.6 if i == 0 else 0.5, color if i == 0 else WHITE, 2 if i == 0 else 1)


# ---------- Main loop ----------

(L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']
landmark_predict = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

marked_today = load_marked_today()
blink_counter = {}
names = []
frame_count = 0

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)  # window always matches the frame, so the banner isn't cut off

while True:
    suc, img = cap.read()
    if not suc:
        print("Could not read from the webcam.")
        break

    img = cv2.flip(img, 1)  # mirror view feels natural
    if img.shape[1] != DISPLAY_W:
        img = cv2.resize(img, (DISPLAY_W, int(img.shape[0] * DISPLAY_W / img.shape[1])))
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    imgS = cv2.resize(img, (0, 0), None, SCALE, SCALE)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # detect every frame (needed for blink tracking), but only re-identify every few frames
    faces = sorted(face_recognition.face_locations(imgS), key=lambda loc: loc[3])
    if frame_count % RECOGNISE_EVERY == 0 or len(faces) != len(names):
        names = [identify(e) for e in face_recognition.face_encodings(imgS, faces)]
    frame_count += 1

    # bottom banner message: blink request > done > unknown > idle
    message, msg_color, msg_rank = "Please look at the camera", WHITE, 0

    for (top, right, bottom, left), name in zip(faces, names):
        x1, y1, x2, y2 = int(left / SCALE), int(top / SCALE), int(right / SCALE), int(bottom / SCALE)

        if name is None:
            cv2.rectangle(img, (x1, y1), (x2, y2), RED, 2)
            put(img, "Unknown", (x1, y1 - 8), 0.6, RED, 2)
            if msg_rank < 1:
                message, msg_color, msg_rank = "Face not recognised - please register first", RED, 1
            continue

        student = students.get(name.lower())
        display_name = student["full_name"] if student else name.replace("_", " ").title()

        if name not in marked_today:
            shape = face_utils.shape_to_np(landmark_predict(gray, dlib.rectangle(x1, y1, x2, y2)))
            avg = (calculate_EAR(shape[L_start:L_end]) + calculate_EAR(shape[R_start:R_end])) / 2

            blink_counter.setdefault(name, 0)
            if avg < blink_thresh:
                blink_counter[name] += 1
            else:
                if blink_counter[name] >= succ_frame:
                    marked_today[name] = attendace(name)
                    print(f"Attendance marked: {name} at {marked_today[name]}")
                blink_counter[name] = 0

        done = name in marked_today
        color = GREEN if done else AMBER

        if student:
            lines = [display_name, f"Roll No : {student['roll_no'] or '-'}",
                     f"Branch  : {student['branch'] or '-'}", f"Semester: {student['semester'] or '-'}"]
        else:
            lines = [display_name, "Not in student database"]
        lines.append(f"Status  : {'PRESENT ' + str(marked_today[name]) if done else 'Waiting for blink'}")

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        draw_info_card(img, (x1, y1, x2, y2), lines, color)

        if not done and msg_rank < 3:
            message, msg_color, msg_rank = f"Hi {display_name}, please BLINK to mark your attendance", AMBER, 3
        elif done and msg_rank < 2:
            message, msg_color, msg_rank = f"Attendance done for {display_name}. You may leave - press Q to quit", GREEN, 2

    shade(img, 0, h - 54, w, h, alpha=0.7)
    put(img, message, (20, h - 20), 0.75, msg_color, 2)
    put(img, "Q: quit", (w - 90, 28), 0.55, WHITE, 1)

    cv2.imshow(WINDOW, img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:  # window closed with the X button
        break

cap.release()
cv2.destroyAllWindows()
