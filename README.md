# Smart Attendance System

**Attendance that marks itself, and can't be fooled by a photo.** The webcam recognises who you are, then waits for you to **blink** before marking you present, so holding up a picture doesn't work.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-68%20landmarks-008000)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)

<!-- Add a screenshot or GIF here, e.g. ![Demo](docs/demo.gif) -->

## Features

- **Live face recognition** from the webcam against a folder of known faces
- **Blink-based liveness check** using dlib's 68 facial landmarks (90%+ blink-detection accuracy in testing)
- **Automatic attendance log** in `attendance.xlsx` with **Name, Date and Time**
- **No duplicates:** each person is marked once per day
- **Add people by adding photos.** No training step needed.

## How it works

```
Webcam frame
   │
   ├─► face_recognition ──► who is this?   (compares against photos in photosss/)
   │
   └─► dlib 68 landmarks ──► eye aspect ratio ──► did they blink?
                                                     │
                       recognised + blinked ─────────┴──► write Name, Date, Time to attendance.xlsx
```

1. `encode_faces.py` turns every image in `photosss/` into a 128-number face embedding and saves them to `encodings.npz`, so the app doesn't re-encode on every start. The **file name becomes the person's name**.
2. Each webcam frame is shrunk to 25% for fast face matching. The closest known face is chosen, and the student's details (roll no, branch, semester) are shown from `students.db`.
3. The eye landmarks give an **Eye Aspect Ratio (EAR)**. When the eyes stay closed for 2+ frames and then reopen, it counts as a blink.
4. A recognised person who blinks is written to `attendance.xlsx`, but only if they aren't already marked for today.

## Getting started

### Prerequisites

- Python 3.8+ and a webcam
- On Windows, `dlib` / `face_recognition` need **CMake** and the **Visual Studio C++ Build Tools**

### Install

```bash
git clone https://github.com/ManasvibaRana/Smart_Attendance_System.git
cd Smart_Attendance_System
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

The landmark model `shape_predictor_68_face_landmarks.dat` is already included.

### Add people

Put one clear, front-facing photo per person in `photosss/`, named after them:

```
photosss/
├── Asha_Patel.jpg
└── Rohan_Shah.png
```

Then encode the photos. Run this again whenever you add, change or remove a photo (only new or changed photos are re-encoded; `--all` re-encodes everything):

```bash
python encode_faces.py
```

Optionally add each student's details (roll no, branch, semester) to the SQLite database `students.db`:

```bash
python add_student.py
```

### Run

```bash
python Recognition.py
```

Look at the camera and blink when asked. Your details and status appear next to your face, and you're marked in `attendance.xlsx`. Press **q** to quit.

To browse the student database and attendance log (with search and today's present/absent count):

```bash
python view_database.py
```

`face.py` is a small standalone demo that draws a box around the face in a single image.

## Project structure

```
Smart_Attendance_System/
├── Recognition.py                         # main app: recognition + blink check + attendance
├── encode_faces.py                        # encodes photosss/ into encodings.npz
├── add_student.py                         # adds student details to students.db
├── database.py                            # SQLite helpers for students.db
├── view_database.py                       # window to browse students + attendance
├── face.py                                # single-image face detection demo
├── photosss/                              # known faces (file name = person's name)
├── shape_predictor_68_face_landmarks.dat  # dlib landmark model
├── encodings.npz                          # generated face embeddings
├── students.db                            # generated student database
└── attendance.xlsx                        # generated attendance log
```

## Tech stack

Python · OpenCV · dlib · face_recognition · SciPy · imutils · pandas · NumPy

## Author

**Manasviba Rana**: [LinkedIn](https://www.linkedin.com/in/manasviba-rana) · [GitHub](https://github.com/ManasvibaRana)
