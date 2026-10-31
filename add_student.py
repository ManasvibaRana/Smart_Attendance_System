"""Add or update a student's details in students.db.

Usage: python add_student.py
"""
import os

import database

PHOTO_DIR = "photosss"

photos = sorted(os.path.splitext(f)[0] for f in os.listdir(PHOTO_DIR))
students = database.get_all_students()

print("Photos in photosss/:")
for p in photos:
    print(f"  - {p}{'  (registered)' if p.lower() in students else ''}")

photo_lookup = {p.lower(): p for p in photos}
while True:
    photo_name = input("\nPhoto name (file name without extension, from the list above): ").strip()
    if photo_name.lower() in photo_lookup:
        photo_name = photo_lookup[photo_name.lower()]
        break
    print(f"No photo named '{photo_name}' in {PHOTO_DIR}/. Please type one of the names listed above.")

full_name = input("Full name: ").strip() or photo_name.replace("_", " ")
roll_no = input("Roll no: ").strip()
branch = input("Branch (e.g. CSE): ").strip()
semester = input("Semester (number): ").strip()

database.add_student(photo_name, full_name, roll_no, branch, int(semester) if semester.isdigit() else None)
print(f"\nSaved {full_name} to {database.DB_FILE}")
