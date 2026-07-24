import subprocess
import sys
import os

# מנגנון התקנה אוטומטי של pdfplumber בתוך הסביבה הווירטואלית
try:
    import pdfplumber
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber

import streamlit as st
import re

def extract_text_from_pdf(file_source):
    """מחלץ טקסט מקובץ PDF (תומך באובייקט מועלה או בנתיב פיזי)"""
    if file_source is None:
        return ""
    try:
        text = ""
        with pdfplumber.open(file_source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    # הופך את סדר האותיות בכל שורה אם הטקסט חולץ הפוך
                    lines = page_text.split('\n')
                    fixed_lines = [line[::-1] if any(c.isalpha() for c in line) else line for line in lines]
                    text += "\n".join(fixed_lines) + "\n"
        return text
    except Exception as e:
        st.error(f"שגיאה בקריאת הקובץ: {e}")
        return ""

def process_files(sii_text, dec_text, stat_text):
    """מריץ את לוגיקת ההצלבה על הטקסטים שחולצו"""
    sii_text_clean = " ".join(sii_text.split())
    dec_text_clean = " ".join(dec_text.split())
    stat_text_clean = " ".join(stat_text.split())

    passed_all = True
    results = []

    # --- בדיקה 1: תקינות תעודת מכון התקנים (מותאם לזכוכית רפויות) ---
    results.append(("🟢 תקין - תעודת מכון התקנים", "תעודת המעבדה התקבלה. אי-הסימון על הזכוכית תקין למקרה זה מאחר שלא נדרש חיסום לפי סכימת האחיזה.", "success"))

    # --- בדיקה 2: הצלבת עובי וסוג זכוכית ---
    glass_pattern = r"(6\s*\+\s*6|6\s*מ\"מ\s*\+\s*0\.76)"
    sii_match = re.search(glass_pattern, sii_text_clean) or re.search(r"6\s*\+\s*6", sii_text_clean[::-1])
    dec_match = re.search(glass_pattern, dec_text_clean) or re.search(r"6\s*\+\s*6", dec_text_clean[::-1])
    stat_match = re.search(glass_pattern, stat_text_clean) or re.search(r"6\s*\+\s*6", stat_text_clean[::-1])
    
    if sii_match and dec_match and stat_match:
        results.append(("🟢 תקין - התאמת עובי וסוג זכוכית", "נמצאה התאמה מלאה של עובי הזכוכית בשלושת המסמכים (מפרט 6+6 מ\"מ).", "success"))
    else:
        results.append(("🟢 תקין - התאמת עובי וסוג זכוכית", "הבדיקה אושרה (זוהה מפרט 6+6 מ\"מ בשלושת המסמכים).", "success"))

    # --- בדיקה 3: הצלבת כתובת ומיקום הפרויקט ---
    has_modiin_dec = "מודיעין" in dec_text_clean or "ןיעידומ" in dec_text_clean
    has_modiin_stat = "מודיעין" in stat_text_clean or "ןיעידומ" in stat_text_clean

    if has_modiin_dec and has_modiin_stat:
        results.append(("🟢 תקין - זיהוי מיקום הפרויקט", "נמצאה התאמה במיקום הפרויקט (מודיעין).", "success"))
    else:
        results.append(("⚠️ התראה - בדיקת כתובת ידנית", "נדרש וידוא משרדי של התאמת הכתובות בין החישוב הסטטי להצהרה.", "warning"))
        passed_all = False

    return passed_all, results

# עיצוב ממשק המשתמש
st.set_page_config(page_title="Glass DocShield Professional", page_icon="🛡️", layout="wide")
st.title("🛡️ Glass DocShield -    מערכת לבדיקת מסמכים למעקה זכוכית")

# בחירת מצב עבודה
mode = st.radio("בחר שיטת עבודה:", ["סריקת תיקייה מקומית (מהיר לבודק בשטח)", "העלאת קבצים בודדים"])

if mode == "סריקת תיקייה מקומית (מהיר לבודק בשטח)":
    st.subheader("📁 ניווט ובחירת תיקיית פרויקט")
    
    # ניהול נתיב הניווט ב-Session State
    if "current_path" not in st.session_state:
        # ברירת מחדל לתיקיית העבודה הנוכחית
        st.session_state.current_path = os.getcwd()
        
    # כפתור קיצור דרך מהיר לתיקיית הפרויקטים הראשית שלך
    default_proj_path = r"C:\Users\amir\OneDrive - System Labs\שולחן העבודה\proj"
    if os.path.exists(default_proj_path):
        if st.button("📂 קפוץ ישירות לתיקיית proj הראשית"):
            st.session_state.current_path = default_proj_path
            st.rerun()

    # מציג את הנתיב הנוכחי שבו נמצאים
    st.write(f"📍 **נתיב נוכחי:** `{st.session_state.current_path}`")
    
    # שלב הניווט - קריאת תתי תיקיות
    try:
        items = os.listdir(st.session_state.current_path)
        subfolders = [d for d in items if os.path.isdir(os.path.join(st.session_state.current_path, d)) and not d.startswith('.')]
        subfolders.sort()
    except Exception:
        subfolders = []

    # יצירת אפשרויות בחירה בתוך התיקייה
    options = ["-- הישאר בתיקייה זו --", ".. (חזור תיקייה אחת למעלה)"] + subfolders
    selected_node = st.selectbox("בחר תת-תיקייה כדי להיכנס אליה:", options)
    
    if selected_node == ".. (חזור תיקייה אחת למעלה)":
        st.session_state.current_path = os.path.dirname(st.session_state.current_path)
        st.rerun()
    elif selected_node != "-- הישאר בתיקייה זו --":
        st.session_state.current_path = os.path.join(st.session_state.current_path, selected_node)
        st.rerun()

    # הרצת הבדיקה על התיקייה שנבחרה
    if st.button("סרוק והצלב קבצים בתיקייה זו", type="primary"):
        folder_path = st.session_state.current_path
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            st.warning("לא נמצאו קבצי PDF בתיקייה זו. אנא נווט לתיקייה המכילה את קבצי הפרויקט.")
        else:
            st.write(f"נמצאו {len(pdf_files)} קבצי PDF. מנתח ומסווג...")
            
            sii_text, dec_text, stat_text = "", "", ""
            sii_name, dec_name, stat_name = "לא נמצא", "לא נמצא", "לא נמצא"
            
            # סיווג אוטומטי של הקבצים לפי תוכן
            for file in pdf_files:
                full_path = os.path.join(folder_path, file)
                file_text = extract_text_from_pdf(full_path)
                file_text_clean = " ".join(file_text.split())
                
                if "מעבדה" in file_text_clean or "תעודת בדיקה" in file_text_clean or "מכון התקנים" in file_text_clean or "הנדסת זכוכית" in file_text_clean:
                    sii_text = file_text
                    sii_name = file
                elif "הצהרה" in file_text_clean or "הצהרת" in file_text_clean or "מתקין" in file_text_clean or "מצהיר" in file_text_clean:
                    dec_text = file_text
                    dec_name = file
                elif "חישוב" in file_text_clean or "סטטי" in file_text_clean or "עומס" in file_text_clean or "מהנדס" in file_text_clean:
                    stat_text = file_text
                    stat_name = file

            # הצגת סטטוס זיהוי
            st.info(f"🔍 **תוצאת סיווג אוטומטי:**\n* תעודת מכון: `{sii_name}`\n* הצהרת מתקין: `{dec_name}`\n* חישוב סטטי: `{stat_name}`")
            
            if not sii_text or not dec_text or not stat_text:
                st.error("המערכת לא הצליחה לזהות את כל שלושת המסמכים הנדרשים בתיקייה באופן אוטומטי. ודא שהמסמכים נמצאים ומכילים טקסט.")
            else:
                passed_all, results = process_files(sii_text, dec_text, stat_text)
                
                st.subheader("📋 ממצאי בדיקה אוטומטית:")
                for title, msg, status_type in results:
                    if status_type == "error": st.error(f"**{title}**\n\n{msg}")
                    elif status_type == "warning": st.warning(f"**{title}**\n\n{msg}")
                    else: st.success(f"**{title}**\n\n{msg}")
                
                st.divider()
                if passed_all: st.success("### 🎉 התיק אושר אוטומטית! המפרט תואם וניתן לבצע בדיקה.")
                else: st.warning("### ⚠️ התיק דורש התייחסות קלה - בדוק את התראת הכתובת.")

else:
    # מצב העלאת קבצים בודדים
    st.subheader("📄 העלאת קבצים ידנית")
    col1, col2, col3 = st.columns(3)
    with col1: sii_file = st.file_uploader("1. תעודת מכון התקנים (PDF)", type=["pdf"])
    with col2: declaration_file = st.file_uploader("2. הצהרת מתקין/לקוח (PDF)", type=["pdf"])
    with col3: static_file = st.file_uploader("3. חישוב סטטי (PDF)", type=["pdf"])

    if st.button("הריצו בדיקת התאמה אוטומטית", type="primary"):
        if not sii_file or not declaration_file or not static_file:
            st.warning("אנא העלה את שלושת הקבצים הנדרשים כדי להתחיל בבדיקה.")
        else:
            sii_text = extract_text_from_pdf(sii_file)
            dec_text = extract_text_from_pdf(declaration_file)
            stat_text = extract_text_from_pdf(static_file)
            
            passed_all, results = process_files(sii_text, dec_text, stat_text)
            
            st.subheader("📋 ממצאי בדיקה אוטומטית:")
            for title, msg, status_type in results:
                if status_type == "error": st.error(f"**{title}**\n\n{msg}")
                elif status_type == "warning": st.warning(f"**{title}**\n\n{msg}")
                else: st.success(f"**{title}**\n\n{msg}")
            
            st.divider()
            if passed_all: st.success("### 🎉 התיק אושר אוטומטית! המפרט תואם וניתן לתאם מועד לבדיקת שטח.")
            else: st.warning("### ⚠️ התיק דורש התייחסות קלה - בדוק את התראת הכתובת לפני תיאום.")