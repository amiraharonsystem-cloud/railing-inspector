import streamlit as str_ui
import json
import random
from bidi.algorithm import get_display

# הגדרת כיווניות טקסט לעברית עבור כותרות מסוימות במידת הצורך
def r_text(text):
    return get_display(str(text))

# ==========================================
# 1. הדמיית מאגרי הנתונים (Mocks)
# ==========================================
if 'magic_projects_db' not in str_ui.session_state:
    str_ui.session_state.magic_projects_db = {"הרצל 100, תל אביב": "PRJ-99281"}

if 'salesforce_orders_db' not in str_ui.session_state:
    str_ui.session_state.salesforce_orders_db = []

testers_db = [
    {"name": "יוסי כהן", "specialty": "כיבוי אש", "region": "תל אביב", "available_dates": ["2026-07-20", "2026-07-21"]},
    {"name": "אבי לוי", "specialty": "איטום", "region": "ראשון לציון", "available_dates": ["2026-07-22"]},
    {"name": "דניאל משה", "specialty": "כיבוי אש", "region": "מרכז", "available_dates": ["2026-07-25"]}
]

# ==========================================
# 2. לוגיקת האוטומציה
# ==========================================
def run_automation_for_email(email_body, sender, has_attachment):
    logs = []
    logs.append(f"📬 קלט: התקבל מייל חדש מ-{sender}")
    
    # שלב 2: פענוח AI [cite: 19]
    logs.append("🧠 [AI] מנתח את תוכן המייל ומחלץ ישויות...")
    address = "הרצל 100, תל אביב" if "הרצל 100" in email_body else "רוטשילד 45, ראשון לציון"
    test_type = "כיבוי אש" if "כיבוי אש" in email_body or "בטיחות" in email_body else "איטום"
    requested_date = "2026-07-20" if "20/07" in email_body or "20.07" in email_body else None
    
    parsed_data = {
        "customer_name": sender.split("@")[0].replace("_", " ").title(),
        "address": address,
        "test_type": test_type,
        "requested_date": requested_date,
        "attachments": ["safety_plan.pdf"] if has_attachment else []
    }
    logs.append(f"✔️ [AI] חולץ מידע מובנה: {json.dumps(parsed_data, ensure_ascii=False)}")
    
    # שלב 3: בדיקת פרויקט במגיק [cite: 25]
    logs.append(f"🔍 [Magic] מחפש פרויקט פעיל לכתובת: {address}...")
    if address in str_ui.session_state.magic_projects_db:
        project_id = str_ui.session_state.magic_projects_db[address]
        logs.append(f"🔗 [Magic] נמצא פרויקט קיים: {project_id}")
    else:
        project_id = f"PRJ-{random.randint(10000, 99999)}"
        str_ui.session_state.magic_projects_db[address] = project_id
        logs.append(f"🆕 [Magic] לא נמצא פרויקט. נפתח פרויקט חדש: {project_id}")
        
    # שלב 4: שיבוץ בודק [cite: 27]
    logs.append(f"📅 [Scheduler] מחפש בודק זמין להתמחות '{test_type}' באזור של '{address}'...")
    tester_name, scheduled_date = None, None
    for tester in testers_db:
        if tester["specialty"] == test_type and (tester["region"] in address or tester["region"] == "מרכז"):
            if requested_date and requested_date in tester["available_dates"]:
                tester_name, scheduled_date = tester["name"], requested_date
                break
            elif tester["available_dates"]:
                tester_name, scheduled_date = tester["name"], tester["available_dates"][0]
                break
                
    if tester_name:
        logs.append(f"✅ [Scheduler] שובץ בהצלחה: {tester_name} לתאריך {scheduled_date}")
    else:
        logs.append("⚠️ [Scheduler] אזהרה: לא נמצא בודק מתאים ופנוי! נדרש שיבוץ ידני.")
        
    # שלב 5: עדכון Salesforce [cite: 29]
    status = "נקבע מועד" if has_attachment else "ממתינה להשלמת מסמכים"
    if not has_attachment:
        logs.append("❌ [Salesforce] אזהרה: חסרים מסמכי חובה לקביעת הבדיקה!")
        
    order_entry = {
        "project_id": project_id,
        "customer": parsed_data["customer_name"],
        "address": parsed_data["address"],
        "test_type": parsed_data["test_type"],
        "tester": tester_name if tester_name else "טרם שובץ",
        "scheduled_date": scheduled_date if scheduled_date else "לא נקבע",
        "status": status
    }
    
    str_ui.session_state.salesforce_orders_db.append(order_entry)
    logs.append(f"💾 [Salesforce] הרשומה עודכנה בהצלחה ב-CRM בסטטוס: '{status}'")
    
    return logs

# ==========================================
# 3. עיצוב ממשק המשתמש (Streamlit Layout)
# ==========================================
str_ui.set_page_config(page_title="דמו אוטומציית הזמנות", layout="wide")

# התיקון כאן: שימוש ב-unsafe_allow_html=True
str_ui.markdown("""
    <style>
    .reportview-container {
        direction: RTL;
        text-align: right;
    }
    div.stButton > button:first-child {
        background-color: #00cc66;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

str_ui.title("🤖 סימולטור אוטומציית קליטת הזמנות בדיקה")
str_ui.write("ממשק דמו המדגים קבלת מייל, פענוח AI, בדיקה במערכת מגיק ושיבוץ ב-Salesforce.")

col1, col2 = str_ui.columns(2)

with col1:
    str_ui.subheader("📝 סימולציית מייל נכנס (Outlook)")
    sender = str_ui.text_input("שולח (Sender):", "israel_israeli@gmail.com")
    subject = str_ui.text_input("נושא המייל (Subject):", "הזמנת בדיקת מערכות כיבוי אש - הרצל 100 תל אביב")
    email_body = str_ui.text_area("גוף המייל (Email Body):", 
                                "שלום, אשמח לתאם בדיקת מערכות כיבוי אש בבניין שלנו ברחוב הרצל 100, תל אביב. התאריך המועדף עלינו הוא 20/07/2026. מצורפת תוכנית בטיחות.")
    has_attachment = str_ui.checkbox("צרף מסמך חובה (הזמנת עבודה / תוכניות בטיחות)", value=True)
    
    if str_ui.button("🚀 הרץ תהליך אוטומציה למייל זה"):
        with str_ui.spinner("מריץ את האוטומציה במערכות..."):
            logs = run_automation_for_email(email_body, sender, has_attachment)
            str_ui.success("הריצה הסתיימה בהצלחה!")
            
            str_ui.subheader("⚙️ יומן ריצה בזמן אמת (Audit Logs)")
            for log in logs:
                str_ui.code(log, language="bash")

with col2:
    str_ui.subheader("📊 מצב מערכת Salesforce CRM (הזמנות שנקלטו)")
    if str_ui.session_state.salesforce_orders_db:
        str_ui.table(str_ui.session_state.salesforce_orders_db)
    else:
        str_ui.info("אין עדיין הזמנות ב-CRM. שלח מייל בצד שמאל כדי לראות את הנתונים נקלטים.")
        
    str_ui.subheader("💾 פרויקטים פעילים במערכת מגיק (Magic)")
    str_ui.json(str_ui.session_state.magic_projects_db)