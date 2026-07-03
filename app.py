import streamlit as st  # type: ignore[import]
import os
import zipfile
from datetime import datetime

# 1. הגדרת תצורת עמוד
st.set_page_config(
    page_title="מערכת בדיקת מעקות",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. הזרקת CSS להתאמת כיווניות מימין לשמאל (RTL)
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

# 4. פרטי הלקוח
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
        
        # לוגיקה משודרגת: יצירת תיקייה ייעודית וספציפית להזמנה זו
        if uploaded_files:
            # ניקוי רווחים או תווים בעייתיים משם הלקוח בשביל יצירת תיקייה תקינה
            folder_name = f"{customer_name}_דוח_{order_number}"
            
            # הגדרת נתיב התיקייה החדשה
            CUSTOMER_DIR = os.path.join("uploaded_images", folder_name)
            
            # יצירת התיקייה הספציפית של הלקוח אם היא לא קיימת עדיין
            if not os.path.exists(CUSTOMER_DIR):
                os.makedirs(CUSTOMER_DIR)
                
            # שמירת כל התמונות ישירות לתוך התיקייה החדשה שנפתחה
            for file in uploaded_files:
                file_path = os.path.join(CUSTOMER_DIR, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            
            st.success(f"📂 נוצרה תיקייה חדשה והתמונות נשמרו בנתיב: {CUSTOMER_DIR}")
        
        st.balloons()
        st.success(f"הדוח עבור הזמנה {order_number} נשמר בהצלחה במערכת!")
    else:
        st.warning("אנא מלא שם לקוח ומספר הזמנה לפני השמירה כדי שנוכל לייצר את התיקייה עבורך.")