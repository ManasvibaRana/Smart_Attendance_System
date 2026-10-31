"""
Encode every photo in photosss/ and save the face embeddings to encodings.npz.

Run this whenever you add, replace or remove a photo:
    python encode_faces.py          # only encodes new / changed photos
    python encode_faces.py --all    # re-encodes everything
"""
import os
import sys

import face_recognition
import numpy as np

PHOTO_DIR = "photosss"
ENCODINGS_FILE = "encodings.npz"
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def load_existing():
    """Return {name: (encoding, mtime)} from a previous run, if any."""
    if not os.path.exists(ENCODINGS_FILE):
        return {}
    data = np.load(ENCODINGS_FILE)
    return {name: (enc, mtime) for name, enc, mtime in zip(data["names"], data["encodings"], data["mtimes"])}


def encode_photo(path):
    """Return the 128-D encoding of the largest face in the photo, or None."""
    img = face_recognition.load_image_file(path)  # already RGB
    locations = face_recognition.face_locations(img)
    if not locations:
        return None
    # if the photo has several faces, use the biggest one
    largest = max(locations, key=lambda l: (l[2] - l[0]) * (l[1] - l[3]))
    return face_recognition.face_encodings(img, [largest])[0]


def main():
    reencode_all = "--all" in sys.argv
    existing = {} if reencode_all else load_existing()

    names, encodings, mtimes = [], [], []
    added = reused = skipped = 0

    for file in sorted(os.listdir(PHOTO_DIR)):
        if not file.lower().endswith(IMAGE_EXTS):
            continue
        name = os.path.splitext(file)[0]
        path = os.path.join(PHOTO_DIR, file)
        mtime = os.path.getmtime(path)

        if name in existing and existing[name][1] == mtime:
            enc = existing[name][0]
            reused += 1
        else:
            enc = encode_photo(path)
            if enc is None:
                print(f"  [skip] no face found in {file}")
                skipped += 1
                continue
            print(f"  [new]  {name}")
            added += 1

        names.append(name)
        encodings.append(enc)
        mtimes.append(mtime)

    removed = len(set(existing) - set(names))
    np.savez(ENCODINGS_FILE, names=np.array(names), encodings=np.array(encodings).reshape(-1, 128), mtimes=np.array(mtimes))
    print(f"\nSaved {len(names)} faces to {ENCODINGS_FILE} "
          f"({added} new, {reused} unchanged, {removed} removed, {skipped} skipped)")


if __name__ == "__main__":
    main()
