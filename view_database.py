"""Simple window to browse the student database and attendance log.

Usage: python view_database.py
"""
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import pandas as pd

import database

ATTENDANCE_FILE = "attendance.xlsx"

TEAL, LIGHT, TEXT, MUTED = "#0F766E", "#EEF6F4", "#1E293B", "#64748B"


def load_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        return pd.DataFrame(columns=["Name", "Date", "Time"])
    df = pd.read_excel(ATTENDANCE_FILE, engine="openpyxl")
    df["Date"] = df["Date"].astype(str).str[:10]
    df["Time"] = df["Time"].astype(str)
    return df.sort_values(["Date", "Time"], ascending=False)


class DatabaseViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Attendance - Database")
        self.geometry("1000x600")
        self.configure(bg="white")
        self._style()

        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(header, text="Smart Attendance Database", font=("Segoe UI", 18, "bold"), fg=TEXT, bg="white").pack(side="left")
        ttk.Button(header, text="Refresh", command=self.refresh).pack(side="right")

        self.summary = tk.Frame(self, bg="white")
        self.summary.pack(fill="x", padx=20, pady=(0, 10))

        search_row = tk.Frame(self, bg="white")
        search_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(search_row, text="Search:", font=("Segoe UI", 10), fg=MUTED, bg="white").pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.fill_tables())
        ttk.Entry(search_row, textvariable=self.search, width=40).pack(side="left", padx=8)

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.students_table = self._table(tabs, ("Roll No", "Full Name", "Branch", "Semester", "Photo Name", "Today"))
        self.attendance_table = self._table(tabs, ("Date", "Time", "Roll No", "Full Name", "Branch", "Semester"))
        tabs.add(self.students_table.master, text="  Students  ")
        tabs.add(self.attendance_table.master, text="  Attendance Log  ")

        self.refresh()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, foreground=TEXT, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=TEAL, foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[("active", TEAL)])
        style.map("Treeview", background=[("selected", "#99D5CC")], foreground=[("selected", TEXT)])
        style.configure("TNotebook", background="white", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(10, 6))
        style.map("TNotebook.Tab", background=[("selected", LIGHT)], foreground=[("selected", TEAL)])
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 4))

    def _table(self, parent, columns):
        frame = tk.Frame(parent, bg="white")
        table = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=140, anchor="w")
        table.tag_configure("odd", background=LIGHT)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return table

    def _stat(self, value, label, color):
        box = tk.Frame(self.summary, bg=LIGHT, padx=18, pady=8)
        box.pack(side="left", padx=(0, 12))
        tk.Label(box, text=value, font=("Segoe UI", 18, "bold"), fg=color, bg=LIGHT).pack(anchor="w")
        tk.Label(box, text=label, font=("Segoe UI", 9), fg=MUTED, bg=LIGHT).pack(anchor="w")

    def refresh(self):
        self.students = database.get_all_students()
        self.attendance = load_attendance()
        today = datetime.now().strftime("%Y-%m-%d")
        self.present_today = set(self.attendance.loc[self.attendance["Date"] == today, "Name"].str.lower())

        for widget in self.summary.winfo_children():
            widget.destroy()
        present = sum(1 for key in self.students if key in self.present_today)
        self._stat(len(self.students), "Registered students", TEXT)
        self._stat(present, f"Present today ({today})", "#15803D")
        self._stat(len(self.students) - present, "Absent today", "#B91C1C")
        self._stat(len(self.attendance), "Total attendance records", TEAL)

        self.fill_tables()

    def fill_tables(self):
        query = self.search.get().strip().lower()

        def matches(values):
            return not query or any(query in str(v).lower() for v in values)

        self.students_table.delete(*self.students_table.get_children())
        rows = sorted(self.students.values(), key=lambda s: s["roll_no"] or "")
        shown = 0
        for s in rows:
            status = "✔ Present" if s["photo_name"].lower() in self.present_today else "✘ Absent"
            values = (s["roll_no"] or "-", s["full_name"], s["branch"] or "-", s["semester"] or "-", s["photo_name"], status)
            if matches(values):
                self.students_table.insert("", "end", values=values, tags=("odd",) if shown % 2 else ())
                shown += 1

        self.attendance_table.delete(*self.attendance_table.get_children())
        shown = 0
        for _, row in self.attendance.iterrows():
            s = self.students.get(str(row["Name"]).lower(), {})
            values = (row["Date"], row["Time"], s.get("roll_no") or "-",
                      s.get("full_name") or str(row["Name"]).replace("_", " ").title(),
                      s.get("branch") or "-", s.get("semester") or "-")
            if matches(values):
                self.attendance_table.insert("", "end", values=values, tags=("odd",) if shown % 2 else ())
                shown += 1


if __name__ == "__main__":
    DatabaseViewer().mainloop()
