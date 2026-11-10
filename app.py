import streamlit as st
import re
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import io

# إعدادات الصفحة
st.set_page_config(page_title="أمان", page_icon="🛡️", layout="centered")

# إخفاء شعار Streamlit وتكبير الخط
# تصميم التطبيق (CSS) - النسخة النهائية
hide_streamlit_style = """
            <style>
            /* إخفاء العناصر الافتراضية */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stStatusWidget"] {visibility: hidden;}
           
            /* لون الخلفية (أبيض مائل للرمادي الفاتح) */
            .stApp {
                background-color: #F8F9FA;
            }
           
            /* لون النصوص (أزرق داكن للقراءة المريحة) */
            h1, h2, h3, p, label, .stMarkdown {
                color: #0B192C !important;
                text-align: right;
            }
           
            /* تكبير الخط الأساسي */
            html, body, [class*="css"]  {
                font-size: 20px !important;
                text-align: right;
            }
           
            /* تنسيق الأزرار (أخضر داكن) */
            .stButton > button {
                background-color: #1E7D32; /* أخضر */
                color: white;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 18px;
                border: none;
                width: 100%;
                font-weight: bold;
            }
           
            /* تأثير عند تمرير الماوس على الزر */
            .stButton > button:hover {
                background-color: #145A23;
                color: white;
            }
           
            /* تنسيق مربع النص */
            .stTextArea textarea {
                background-color: #FFFFFF;
                color: #0B192C;
                border-radius: 10px;
                border: 2px solid #1E7D32;
            }
           
            /* تنسيق التنبيهات */
            .stAlert {
                border-radius: 10px;
                border-right: 5px solid #1E7D32; /* خط أخضر على اليمين */
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# عرض اللوجو
st.image("logo.png", width=200)

# عنوان التطبيق
st.title("تطبيق أمان")
st.write("أهلاً بك! إما أن تضغط على زر المايك وتتحدث، أو تكتب الرسالة في المربع.")

# 1. زر التسجيل الصوتي
audio_bytes = audio_recorder(text="اضغط على المايك وتحدث", recording_color="#e83e2a", neutral_color="#ffffff", icon_size="2x")

message = ""

# إذا تم تسجيل صوت
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = r.record(source)
            text_from_audio = r.recognize_google(audio_data, language="ar-SA")
            st.success(f"تم التعرف على النص: {text_from_audio}")
            message = text_from_audio
    except Exception as e:
        st.error("عذراً، لم نتمكن من التعرف على الصوت. جرب الكتابة أو أعد التسجيل.")
        message = ""

# 2. خيار الكتابة
message_text = st.text_area("أو اكتب الرسالة هنا:", value=message, height=100)
if message_text:
    message = message_text

# 3. زر التحليل
if st.button("تحليل الرسالة", use_container_width=True):
    if message:
        score = 0
        reasons = []

        # فحص الكلمات المفتاحية
        suspicious_words = ["جائزة", "جائزه", "فزت", "ربحت", "بنك", "الراجحي", "أرسل الرمز", "الرمز السري", "حسابك موقوف", "شحنة", "مكافأة", "عاجل", "أبشر", "تحديث بيانات", "بطاقة"]
        found_words = [word for word in suspicious_words if word in message]
        
        if found_words:
            score += 3
            reasons.append(f"وجود كلمات حساسة ({', '.join(found_words)})")

        # فحص طلب معلومات سرية
        if re.search(r"(رمز|كود|OTP|OTP).*(تحقق|سري)", message, re.IGNORECASE):
            score += 4
            reasons.append("طلب رمز تحقق (OTP) أو معلومات سرية")

        # فحص الروابط
        urls = re.findall(r'(https?://\S+|www\.\S+)', message)
        if urls:
            score += 2
            reasons.append("وجود رابط إلكتروني في الرسالة")
            if any(short in urls[0].lower() for short in ["bit.ly", "tinyurl", "t.co", "goo.gl"]):
                score += 3
                reasons.append("رابط مختصر مشبوه (يخفي الوجهة الحقيقية)")

        # إعطاء النتيجة
        if score >= 6:
                    if score >= 6:
    st.error("🚨 تحذير! توجد مؤشرات قوية على محاولة احتيال!")

    st.markdown(
        """
        <div style="
            background-color:#ffdddd;
            color:#990000;
            padding:20px;
            border-radius:12px;
            text-align:center;
            font-size:24px;
            font-weight:bold;
            border:3px solid red;
        ">
            🚨 إنذار أمان 🚨<br>
            احذر! لا تضغط على الروابط ولا تشارك بياناتك السرية.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("**أسباب التحذير:**")
    for reason in reasons:
        st.write(f"- {reason}")

    # تشغيل صوت الإنذار
    try:
        with open("warning.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()

        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    except FileNotFoundError:
        st.warning("ملف الإنذار warning.mp3 غير موجود.")

    st.write("تواصل مع الجهة الرسمية للتأكد.")

