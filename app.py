import streamlit as st  # type: ignore[import]
import os
from datetime import datetime

# 1. הגדרת תצורת עמוד
st.set_page_config(
    page_title="מערכת בדיקת מעקות",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. הזרקת CSS להתאמת כיווניות מימין לשמאל (RTL) ותצוגה נקייה
st.markdown("""
    <style>
    body, .stApp, p, li, h1, h2, h3, h4, h5, div, label {
        direction: RTL;
        text-align: right;
    }
    div[data-testid="stBlock"] {
        direction: RTL;
    }
    input, textarea, select {
        direction: RTL !important;
        text-align: right !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. כותרת האפליקציה
st.title("מערכת בדיקת מעקות - ת ק 1142")
st.write(f"תאריך עדכון המערכת: {datetime.now().strftime('%d/%m/%Y')}")
st.divider()

# 4. פרטי הלקוח וזיהוי ההזמנה
st.header("1. פרטי הלקוח וזיהוי ההזמנה")

col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("שם הלקוח / החברה המזמינה:")
    project_name = st.text_input("שם הפרויקט / אתר הבדיקה:")
with col2:
    order_number = st.text_input("מספר הזמנה / דוח:")
    inspector_name = st.text_input("שם הבודק:")

# 5. אזור בדיקת המעקה בשטח
st.divider()
st.header("2. ממצאי בדיקת המעקה בשטח")

railing_height = st.number_input("גובה מעקה נמדד (בס\"מ):", min_value=0.0, max_value=200.0, value=105.0)
gap_size = st.number_input("מרווח מקסימלי בין רכיבים אנכיים (בס\"מ):", min_value=0.0, max_value=50.0, value=10.0)

st.subheader("סטטוס עמידה בתקן:")
if railing_height >= 105 and gap_size <= 10:
    st.success("המערכת עומדת בדרישות תקן 1142")
else:
    st.error("המערכת אינה עומדת בדרישות התקן")

# 6. תיעוד גרפי ותמונות מהשטח
st.divider()
st.header("3. תיעוד גרפי ותמונות מהשטח")

uploaded_files = st.file_uploader(
    "גרור או בחר תמונות של המעקה/הליקויים:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"הועלו {len(uploaded_files)} תמונות זמניות:")
    cols = st.columns(2)
    for index, file in enumerate(uploaded_files):
        with cols[index % 2]:
            st.image(file, caption=f"תמונה {index + 1}: {file.name}", use_container_width=True)

# 7. הערות וסיכום
st.divider()
notes = st.text_area("הערות נוספות וממצאים מיוחדים:")

if st.button("שמור דוח בדיקה"):
    if customer_name and order_number:
        
        # הגדרת נתיב מוחלט ומדויק ישירות לתוך תיקיית ה-OneDrive של המערכת
        BASE_ONEDRIVE_PATH = r"C:\Users\amir\OneDrive - System Labs\שולחן העבודה\proj"
        IMAGE_FOLDER_PATH = os.path.join(BASE_ONEDRIVE_PATH, "uploaded_images")
        
        # יצירת התיקייה הראשית ב-OneDrive אם היא לא קיימת
        if not os.path.exists(IMAGE_FOLDER_PATH):
            os.makedirs(IMAGE_FOLDER_PATH)
            
        # יצירת תיקייה ספציפית ללקוח הנוכחי
        customer_folder_name = f"{customer_name}_דוח_{order_number}"
        CUSTOMER_DIR = os.path.join(IMAGE_FOLDER_PATH, customer_folder_name)
        
        if not os.path.exists(CUSTOMER_DIR):
            os.makedirs(CUSTOMER_DIR)
            
        # שמירת הקבצים פיזית לתיקייה החדשה ב-OneDrive
        if uploaded_files:
            for file in uploaded_files:
                file_path = os.path.join(CUSTOMER_DIR, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            st.success(f"📂 נוצרה תיקייה והתמונות נשמרו ב-OneDrive בנתיב: {CUSTOMER_DIR}")
        else:
            st.info(f"📂 נוצרה תיקיית דוח ריקה ב-OneDrive בנתיב: {CUSTOMER_DIR}")
        
        st.balloons()
        st.success(f"הדוח עבור הזמנה {order_number} נשמר בהצלחה!")
    else:
        st.warning("אנא מלא שם לקוח ומספר הזמנה לפני השמירה.")