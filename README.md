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

1. On start, every image in `photosss/` is encoded. The **file name becomes the person's name**.
2. Each webcam frame is shrunk to 25% for fast face matching. The closest known face is chosen.
3. The eye landmarks give an **Eye Aspect Ratio (EAR)**. When the eyes stay closed for 2+ frames and then reopen, it counts as a blink.
4. A recognised person who blinks is written to `attendance.xlsx`, but only if they aren't already marked for today.

## Getting started

### Prerequisites

- Python 3.8+ and a webcam
- On Windows, `dlib` / `face_recognition` need **CMake** and the **Visual Studio C++ Build Tools**

### Install

```bash
git clone https://github.com/ManasvibaRana/Smart_Attendace_System.git
cd Smart_Attendace_System
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

### Run

```bash
python Recognition.py
```

Look at the camera and blink. You'll be marked in `attendance.xlsx`. Press **q** to quit.

`face.py` is a small standalone demo that draws a box around the face in a single image.

## Project structure

```
Smart_Attendace_System/
├── Recognition.py                         # main app: recognition + blink check + attendance
├── face.py                                # single-image face detection demo
├── photosss/                              # known faces (file name = person's name)
├── shape_predictor_68_face_landmarks.dat  # dlib landmark model
└── attendance.xlsx                        # generated attendance log
```

## Tech stack

Python · OpenCV · dlib · face_recognition · SciPy · imutils · pandas · NumPy

## Author

**Manasviba Rana**: [LinkedIn](https://www.linkedin.com/in/manasviba-rana) · [GitHub](https://github.com/ManasvibaRana)
