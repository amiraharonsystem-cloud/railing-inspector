import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

# ----------------- 1. הגדרת בסיס הנתונים -----------------


def init_db():
    conn = sqlite3.connect("work_schedule.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            employee_name TEXT NOT NULL,
            client_name TEXT NOT NULL,
            client_phone TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# ----------------- 2. לוגיקה וארועים -----------------


def add_shift():
    date = entry_date.get()
    employee = entry_employee.get()
    client = entry_client.get()
    phone = entry_phone.get()
    start = entry_start.get()
    end = entry_end.get()

    if not (date and employee and client and phone and start and end):
        messagebox.showwarning("שגיאה", "אנא מלא את כל השדות!")
        return

    conn = sqlite3.connect("work_schedule.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO schedule (date, employee_name, client_name, client_phone, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (date, employee, client, phone, start, end),
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("הצלחה", "המשמרת נוספה בהצלחה!")
    clear_entries()
    load_data()


def load_data(query_filter=""):
    # ניקוי הטבלה הקיימת
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("work_schedule.db")
    cursor = conn.cursor()

    if query_filter:
        cursor.execute(
            """
            SELECT * FROM schedule 
            WHERE client_name LIKE ? OR client_phone LIKE ? OR employee_name LIKE ?
            ORDER BY date DESC
        """,
            (f"%{query_filter}%", f"%{query_filter}%", f"%{query_filter}%"),
        )
    else:
        cursor.execute("SELECT * FROM schedule ORDER BY date DESC")

    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)

    conn.close()


def delete_shift():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("שגיאה", "אנא בחר משמרת למחיקה מהטבלה")
        return

    shift_id = tree.item(selected_item)["values"][0]

    if messagebox.askyesno("אישור", "האם אתה בטוח שברצונך למחוק משמרת זו?"):
        conn = sqlite3.connect("work_schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedule WHERE id = ?", (shift_id,))
        conn.commit()
        conn.close()
        load_data()


def open_whatsapp():
    """פותח שיחת WhatsApp עם הלקוח של המשמרת שנבחרה"""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("שגיאה", "אנא בחר משמרת מהטבלה כדי לשלוח הודעה")
        return

    values = tree.item(selected_item)["values"]
    client_name = values[3]
    phone = str(values[4])
    date = values[1]
    start_time = values[5]

    # ניקוי מספר הטלפון מתווים שאינם ספרות
    clean_phone = "".join(filter(str.isdigit, phone))

    # התאמת קידומת בינלאומית לישראל אם המספר מתחיל ב-0
    if clean_phone.startswith("0"):
        clean_phone = "972" + clean_phone[1:]

    # הודעה מובנית מראש
    message = f"שלום {client_name}, תזכורת לגבי המשמרת/פגישה בתאריך {date} בשעה {start_time}."

    # פתיחת הקישור בדפדפן
    whatsapp_url = (
        f"https://wa.me/{clean_phone}?text={webbrowser.quote(message)}"
    )
    webbrowser.open(whatsapp_url)


def search_data():
    search_term = entry_search.get()
    load_data(search_term)


def clear_entries():
    entry_date.delete(0, tk.END)
    entry_employee.delete(0, tk.END)
    entry_client.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_start.delete(0, tk.END)
    entry_end.delete(0, tk.END)


# ----------------- 3. ממשק משתמש (GUI) -----------------

init_db()

root = tk.Tk()
root.title("מערכת לניהול סידור עבודה ולקוחות")
root.geometry("850x650")

# טופס הזנת נתונים (תוקן ל-ttk.LabelFrame)
frame_form = ttk.LabelFrame(root, text="הוספת משמרת חדשה", padding=10)
frame_form.pack(fill="x", padx=15, pady=10)

labels = [
    "תאריך (YYYY-MM-DD):",
    "שם עובד:",
    "שם לקוח:",
    "טלפון לקוח:",
    "שעת התחלה:",
    "שעת סיום:",
]
entries = []

for i, label_text in enumerate(labels):
    row = i // 2
    col = (i % 2) * 2

    lbl = ttk.Label(frame_form, text=label_text)
    lbl.grid(row=row, column=col, sticky="e", padx=5, pady=5)

    entry = ttk.Entry(frame_form, justify="right")
    entry.grid(row=row, column=col + 1, sticky="w", padx=5, pady=5)
    entries.append(entry)

(
    entry_date,
    entry_employee,
    entry_client,
    entry_phone,
    entry_start,
    entry_end,
) = entries

btn_add = tk.Button(
    frame_form,
    text="הוסף משמרת",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    command=add_shift,
)
btn_add.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

# אזור חיפוש (תוקן ל-ttk.Frame)
frame_search = ttk.Frame(root, padding=5)
frame_search.pack(fill="x", padx=15)

lbl_search = ttk.Label(frame_search, text="חיפוש (לקוח/טלפון/עובד):")
lbl_search.pack(side="right", padx=5)

entry_search = ttk.Entry(frame_search, justify="right")
entry_search.pack(side="right", fill="x", expand=True, padx=5)

btn_search = ttk.Button(frame_search, text="חפש", command=search_data)
btn_search.pack(side="right", padx=5)

btn_reset = ttk.Button(
    frame_search, text="הצג הכל", command=lambda: load_data()
)
btn_reset.pack(side="right", padx=5)

# טבלת נתונים
columns = (
    "id",
    "date",
    "employee",
    "client",
    "phone",
    "start_time",
    "end_time",
)
tree = ttk.Treeview(root, columns=columns, show="headings")

tree.heading("id", text="מזהה")
tree.heading("date", text="תאריך")
tree.heading("employee", text="שם עובד")
tree.heading("client", text="שם לקוח")
tree.heading("phone", text="טלפון לקוח")
tree.heading("start_time", text="התחלה")
tree.heading("end_time", text="סיום")

tree.column("id", width=40, anchor="center")
tree.column("date", width=90, anchor="center")
tree.column("employee", width=120, anchor="center")
tree.column("client", width=120, anchor="center")
tree.column("phone", width=110, anchor="center")
tree.column("start_time", width=70, anchor="center")
tree.column("end_time", width=70, anchor="center")

tree.pack(fill="both", expand=True, padx=15, pady=10)

# אזור כפתורי פעולה בתחתית
frame_actions = ttk.Frame(root, padding=5)
frame_actions.pack(fill="x", padx=15, pady=5)

btn_whatsapp = tk.Button(
    frame_actions,
    text="💬 שלח WhatsApp ללקוח שנבחר",
    bg="#25D366",
    fg="white",
    font=("Arial", 10, "bold"),
    command=open_whatsapp,
)
btn_whatsapp.pack(side="right", padx=5)

btn_delete = tk.Button(
    frame_actions,
    text="🗑️ מחק משמרת שנבחרה",
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    command=delete_shift,
)
btn_delete.pack(side="left", padx=5)

# טעינת נתונים ראשונית
load_data()

# הרצת האפליקציה
root.mainloop()