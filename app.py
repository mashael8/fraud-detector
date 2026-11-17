import streamlit as st
import re
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import io
import base64

# إعدادات الصفحة
st.set_page_config(
    page_title="أمان",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إخفاء شعار Streamlit وتكبير الخط
# تصميم التطبيق (CSS) - النسخة النهائية


hide_streamlit_style = """
<style>
/* الخلفية الرئيسية */
.stApp {
    background: linear-gradient(135deg, #061426, #0B2545, #071A30);
}

/* إخفاء عناصر Streamlit */
#MainMenu, footer, header,
[data-testid="stStatusWidget"] {
    visibility: hidden;
}

/* اتجاه ومحاذاة النصوص */
h1, h2, h3, p, label, .stMarkdown,
.stText, span {
    color: #EAF6FF !important;
    text-align: right;
}

/* عنوان تسجيل الدخول */
h1 {
    font-size: 44px !important;
    font-weight: bold !important;
    margin-bottom: 18px !important;
}

/* الخط الأساسي */
html, body, [class*="css"] {
    font-size: 18px !important;
}

/* حقول الإدخال */
.stTextInput input,
.stTextArea textarea {
    background-color: #102B49 !important;
    color: white !important;
    border: 1px solid #00B8D9 !important;
    border-radius: 12px !important;
    min-height: 52px;
    font-size: 18px !important;
    text-align: right !important;
}

/* إطار الحقول عند التحديد */
.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 2px solid #00E0C6 !important;
    box-shadow: 0 0 12px rgba(0, 224, 198, 0.25);
}

/* تسميات الحقول */
.stTextInput label {
    color: #EAF6FF !important;
    font-size: 18px !important;
}

/* الأزرار */
.stButton > button {
    background: linear-gradient(90deg, #00B8D9, #00E0C6);
    color: #041525 !important;
    border: 1px solid #00E0C6;
    border-radius: 14px;
    padding: 12px 28px;
    font-size: 18px;
    font-weight: bold;
    width: auto;
    min-height: 52px;
    box-shadow: 0 0 14px rgba(0, 224, 198, 0.3);
}

/* تأثير المرور */
.stButton > button:hover {
    background: #00E0C6;
    color: #041525 !important;
    box-shadow: 0 0 22px rgba(0, 224, 198, 0.6);
    border-color: #00E0C6;
}

/* البطاقات */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(16, 43, 73, 0.65);
    border: 1px solid rgba(0, 184, 217, 0.25);
    border-radius: 15px;
}

/* التنبيهات */
.stAlert {
    border-radius: 12px;
}

/* الشعار */
[data-testid="stImage"] {
    margin-bottom: 20px;
}

/* ضبط المسافة العلوية للصفحة */
.block-container {
    padding-top: 7rem !important;
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# ===== نظام الدخول التجريبي =====

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if "users" not in st.session_state:
    st.session_state.users = {}


if not st.session_state.logged_in:
    st.image("logo.png", width=130)

    if st.session_state.show_signup:
        st.title("إنشاء حساب جديد")
        st.write("أنشئ حسابك للانضمام إلى أمان")

        new_email = st.text_input("البريد الإلكتروني الجديد")
        new_password = st.text_input("كلمة المرور الجديدة", type="password")
        confirm_password = st.text_input("تأكيد كلمة المرور", type="password")

        if st.button("إنشاء الحساب"):
            if not new_email or not new_password or not confirm_password:
                st.warning("الرجاء تعبئة جميع الحقول")
            elif new_password != confirm_password:
                st.error("كلمتا المرور غير متطابقتين")
            elif new_email in st.session_state.users:
                st.error("هذا البريد مسجل مسبقاً")
            else:
                st.session_state.users[new_email] = new_password
                st.session_state.logged_in = True
                st.session_state.show_signup = False
                st.success("تم إنشاء حسابك بنجاح!")
                st.rerun()

        if st.button("العودة إلى تسجيل الدخول"):
            st.session_state.show_signup = False
            st.rerun()

    else:
        st.title("تسجيل الدخول إلى أمان")
        st.write("مرحباً بك، سجّل الدخول للمتابعة")

        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")

        if st.button("تسجيل الدخول"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة")

        st.write("ليس لديك حساب؟")

        if st.button("إنشاء حساب"):
            st.session_state.show_signup = True
            st.rerun()

    st.stop()

# ===== نهاية نظام الدخول =====

# زر تسجيل الخروج
if st.session_state.logged_in:
    st.sidebar.markdown("### حسابك")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.show_signup = False
        st.rerun()
                
# عرض اللوجو
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])

with logo_col2:
    st.image("logo.png", width=150)

# التبويبات
tab1 = st.container(border=True)
# عنوان التطبيق
st.markdown(
    """
    <h1 style="
        text-align:center;
        color:#00E0C6;
        font-size:36px;
        font-weight:bold;
        margin-top:20px;
    ">
        أمان – نظام الفحص الشامل
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <p style="
        text-align:center;
        color:#B8D9F2;
        font-size:18px;
        margin-bottom:25px;
    ">
        مرحباً بك في أمان. أدخل الرسالة أو الرابط الذي تريد فحصه،
        وسنساعدك على اكتشاف مؤشرات الاحتيال.
    </p>
    """,
    unsafe_allow_html=True
)

# 1. زر التسجيل الصوتي
audio_bytes = audio_recorder(
    text="اضغط هنا للتسجيل الصوتي",
    recording_color="#00E0C6",
    neutral_color="#00B8D9",
    icon_size="2x"
)

message = ""

with tab1:
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
    message_text = st.text_area(
    "الرسالة أو الرابط المراد فحصه",
    value=message,
    height=200,
    placeholder="الصق الرسالة أو الرابط هنا للتحقق من سلامته..."
)
    if message_text:
        message = message_text
    # 3. زر التحليل
    if st.button("ابدأ الفحص الشامل", use_container_width=True):
        if message:
            score = 0
            reasons = []

        
            # فحص الكلمات والعبارات المشبوهة
            suspicious_words = [
                # الجوائز والإغراءات
                "جائزة", "جائزه", "فزت", "ربحت", "مبروك", "هدية مجانية",
                "سحب", "اربح", "كسبت", "جائزة نقدية",

                # التهديد والاستعجال
                "حسابك موقوف", "حسابك مغلق", "سيتم إيقاف حسابك",
                "آخر فرصة", "عاجل", "فورا", "خلال 24 ساعة",
                "اتخذ إجراء", "تأكيد الحساب",

                # البنوك والمدفوعات
                "البنك", "الراجحي", "الأهلي", "بنك الرياض",
                "تحديث بيانات", "بيانات البطاقة", "بطاقتك البنكية",
                "عملية مشبوهة", "استرداد مبلغ", "حوالة مالية",

                # المعلومات السرية
                "الرمز السري", "رمز التحقق", "رمز التأكيد",
                "كلمة المرور", "الرقم السري", "بيانات الدخول",
                "أرسل الرمز", "شارك الرمز", "كود التحقق",

                # الشحن والتوصيل
                "شحنتك معلقة", "تعذر تسليم الشحنة",
                "رسوم التوصيل", "تأكيد عنوانك", "طردك",

                # انتحال الجهات
                "أبشر", "نفاذ", "وزارة الداخلية",
                "مؤسسة النقد", "البريد السعودي"
            ]

            found_words = [
                word for word in suspicious_words
                if word in message
            ]

            if found_words:
                score += 3
                reasons.append(
                    f"وجود عبارات مشبوهة ({', '.join(found_words)})"
                )


        
            # فحص طلب المعلومات السرية
            sensitive_patterns = [
                r"(رمز|كود|otp).*(تحقق|تأكيد|سري)",
                r"(تحقق|تأكيد).*(رمز|كود|otp)",
                r"(أرسل|ارسل|شارك|أدخل|ادخل).*(رمز|كود|كلمة المرور|الرقم السري)",
                r"(كلمة المرور|الرقم السري|بيانات الدخول)",
                r"(رقم البطاقة|تاريخ الانتهاء|رمز cvv)",
                r"(بياناتك البنكية|معلوماتك المصرفية)"
            ]

            if any(re.search(pattern, message, re.IGNORECASE)
                   for pattern in sensitive_patterns):
                score += 4
                reasons.append("طلب معلومات سرية أو بيانات بنكية")


       
            
            # فحص الروابط
            urls = re.findall(
                r'(https?://[^\s]+|www\.[^\s]+)',
                message,
                re.IGNORECASE
            )

            if urls:
                score += 2
                reasons.append("وجود رابط إلكتروني في الرسالة")

                suspicious_domains = [
                    "bit.ly", "tinyurl.com", "t.co",
                    "goo.gl", "is.gd", "cutt.ly",
                    "rb.gy", "ow.ly"
                ]

                for url in urls:
                    if any(domain in url.lower() for domain in suspicious_domains):
                        score += 3
                        reasons.append("وجود رابط مختصر قد يخفي الوجهة الحقيقية")
                        break

                suspicious_extensions = [
                    ".xyz", ".top", ".click", ".work"
                ]

                if any(
                    ext in item.lower()
                    for item in urls
                    for ext in suspicious_extensions
                ):
                    score += 2
                    reasons.append("وجود نطاق يستحق التحقق منه")

        
        
        # إعطاء النتيجة
        if score >= 6:
            st.error("🚨 تحذير! توجد مؤشرات قوية على محاولة احتيال!")

            st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #3B101B, #641B2B);
        color: #FFFFFF;
        padding: 22px;
        border-radius: 16px;
        text-align: center;
        font-size: 23px;
        font-weight: bold;
        border: 2px solid #FF4D5A;
        box-shadow: 0 0 18px rgba(255, 77, 90, 0.35);
    ">
        🚨 إنذار أمان 🚨<br>
        احذر! لا تضغط على الروابط ولا تشارك بياناتك السرية.
    </div>
    """,
    unsafe_allow_html=True
)
            )

            st.write("**أسباب التحذير:**")
            for reason in reasons:
                st.write(f"- {reason}")

            try:
                with open("warning.mp3", "rb") as audio_file:
                    audio_bytes = audio_file.read()

                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

                components.html(
                    f"""
                    <audio autoplay>
                        <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
                    </audio>
                    """,
                    height=0
                )

            except FileNotFoundError:
                st.warning("ملف الإنذار warning.mp3 غير موجود.")

        elif score >= 3:
            st.warning("⚠️ تنبيه! توجد مؤشرات تستدعي الحذر.")
            st.write("**أسباب التنبيه:**")
            for reason in reasons:
                st.write(f"- {reason}")
            st.write("لا تضغط على الروابط ولا تشارك بياناتك السرية.")

        else:
            st.success("✅ لم نعثر على مؤشرات احتيال قوية.")
            st.write("كن حذرًا دائمًا، ولا تشارك بياناتك الشخصية أو رموز التحقق.")

    else:
        st.warning("الرجاء إدخال رسالة أولاً.")
