import urllib.parse
import streamlit as st

# הגדרת כותרת העמוד וסימניה בדפדפן
st.set_page_config(page_title="ניווט ל-Waze", page_icon="🚗", layout="centered")

# עיצוב מותאם בעברית (RTL)
st.markdown(
    """
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    input {
        text-align: right;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🚗 ניווט ל-Waze")
st.write("הכנס כתובת כדי ליצור כפתור ניווט מהיר:")

# שדה קלט לכתובת
address = st.text_input("כתובת בישראל", placeholder="למשל: דיזנגוף 50, תל אביב")

# אם המשתמש הזין כתובת - מייצרים את הקישור והכפתור
if address.strip():
    encoded_address = urllib.parse.quote(address)
    waze_url = f"https://www.waze.com/live-map/directions?q={encoded_address}"

    st.markdown("---")
    st.success(f"הכתובת התקבלה: **{address}**")

    # כפתור שפותח את Waze בחלון חדש
    st.link_button(
        "🚗 לחץ כאן לניווט ב-Waze", waze_url, use_container_width=True
    )