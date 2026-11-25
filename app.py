import streamlit as st
import re
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import io
import base64
from pathlib import Path
from PIL import Image
import pytesseract

# إعدادات الصفحة
st.set_page_config(
    page_title="أمان",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# تصميم التطبيق (CSS)
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
/* تأثير البطاقة الزجاجية */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(16, 43, 73, 0.55) !important;
    border: 1px solid rgba(0, 224, 198, 0.35) !important;
    border-radius: 22px !important;
    box-shadow:
        0 0 20px rgba(0, 224, 198, 0.12),
        inset 0 0 20px rgba(0, 184, 217, 0.05) !important;
    padding: 20px !important;
}

/* تحسين العرض على الجوال */
@media screen and (max-width: 768px) {

    .block-container {
        padding: 1rem 0.8rem !important;
        max-width: 100% !important;
    }

    h1 {
        font-size: 27px !important;
        line-height: 1.5 !important;
    }

    h2, h3 {
        font-size: 22px !important;
    }

    p, label, .stMarkdown {
        font-size: 16px !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        width: 100% !important;
        font-size: 16px !important;
    }

    .stButton > button {
        width: 100% !important;
        min-height: 50px !important;
        font-size: 16px !important;
    }

    [data-testid="stImage"] img {
        max-width: 120px !important;
        height: auto !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
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
    logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])

    with logo_col2:
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
        show_password = st.checkbox("إظهار كلمة المرور")

        password = st.text_input(
            "كلمة المرور",
            type="default" if show_password else "password"
        )

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

# زر تسجيل الخروج أعلى الصفحة
col1, col2 = st.columns([5, 1])

with col2:
    if st.button("تسجيل الخروج"):
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
        مرحباً بك في أمان. افحص الرسائل والروابط أو ارفع صورة تحتوي على رسالة أو رابط.
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
uploaded_image = None

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

    # 2. رفع صورة لفحص النصوص والروابط الموجودة بداخلها
    uploaded_image = st.file_uploader(
        "أو ارفع صورة رسالة أو إعلان لفحصها",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="الصورة المرفوعة", use_container_width=True)

    # 3. خيار الكتابة
    message_text = st.text_area(
    "الرسالة أو الرابط المراد فحصه",
    value=message,
    height=200,
    placeholder="الصق الرسالة أو الرابط هنا للتحقق من سلامته..."
)
    if message_text:
        message = message_text
    # 4. زر التحليل
    if st.button("ابدأ الفحص الشامل", use_container_width=True):
        if message or uploaded_image is not None:
            score = 0
            reasons = []

            # استخراج النص من الصورة (OCR) ثم فحصه مع الرسالة والروابط
            if uploaded_image is not None:
                try:
                    image = Image.open(uploaded_image).convert("RGB")
                    image_text = pytesseract.image_to_string(image, lang="ara+eng")
                    if image_text.strip():
                        message = (message + "\n" + image_text).strip()
                        st.success("تم استخراج النص من الصورة وإضافته للفحص.")
                        with st.expander("النص المستخرج من الصورة"):
                            st.write(image_text)
                    else:
                        st.warning("لم يتم العثور على نص واضح داخل الصورة؛ لا يمكن تقييمها اعتمادًا على الصورة وحدها.")
                        if not message.strip():
                            st.stop()
                except Exception as e:
                    st.error("تعذر قراءة نص الصورة. تأكدي من إعداد OCR ومكتباته.")
                    st.caption(str(e))
                    if not message.strip():
                        st.stop()

        
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
    r'(https?://[^\s]+|www\.[^\s]+|(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|is\.gd|cutt\.ly|rb\.gy|ow\.ly)/[^\s]+)',
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

        
        
        
                        

            # إعطاء النتيجة ودرجة الخطورة

            if score >= 6:

                st.error("🚨 تحذير! توجد مؤشرات قوية على محاولة احتيال!")

                st.markdown(
                    f"""
                    <div style="background:#641B2B; border:2px solid #FF4D5A;
                    border-radius:15px; padding:20px; text-align:center;">
                        <div style="color:white;font-size:20px;">مستوى الخطورة</div>
                        <div style="color:#FF5252;font-size:35px;font-weight:bold;">
                            مرتفع 🔴
                        </div>
                        <div style="color:white;font-size:22px;">
                            درجة الخطورة: {score} نقطة
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("**أسباب التحذير:**")
                for reason in reasons:
                    st.write(f"- {reason}")

                # تشغيل صوت الإنذار
                try:
                    warning_path = Path(__file__).resolve().parent / "warning.mp3"

                    if warning_path.exists():
                        audio_base64 = base64.b64encode(
                            warning_path.read_bytes()
                        ).decode("utf-8")

                        components.html(
                            f"""
                            <audio autoplay>
                                <source src="data:audio/mpeg;base64,{audio_base64}"
                                type="audio/mpeg">
                            </audio>
                            """,
                            height=0
                        )
                    else:
                        st.warning("ملف الإنذار warning.mp3 غير موجود.")

                except Exception as e:
                    st.warning(f"تعذر تشغيل الإنذار: {e}")

            elif score >= 3:

                st.warning("⚠️ توجد مؤشرات تستدعي الحذر.")

                st.markdown(
                    f"""
                    <div style="background:#594316; border:2px solid #FFC107;
                    border-radius:15px; padding:20px; text-align:center;">
                        <div style="color:white;font-size:20px;">مستوى الخطورة</div>
                        <div style="color:#FFD54F;font-size:30px;font-weight:bold;">
                            متوسط 🟡
                        </div>
                        <div style="color:white;font-size:21px;">
                            درجة الخطورة: {score} نقطة
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("**أسباب التنبيه:**")
                for reason in reasons:
                    st.write(f"- {reason}")

                st.write("لا تضغط على الروابط ولا تشارك بياناتك السرية.")

            else:

                st.success("✅ لم نعثر على مؤشرات احتيال قوية في المحتوى المفحوص.")

                st.markdown(
                    f"""
                    <div style="background:#123D35; border:2px solid #00E0A0;
                    border-radius:15px; padding:20px; text-align:center;">
                        <div style="color:white;font-size:20px;">مستوى الخطورة</div>
                        <div style="color:#00E0A0;font-size:30px;font-weight:bold;">
                            منخفض 🟢
                        </div>
                        <div style="color:white;font-size:21px;">
                            درجة الخطورة: {score} نقطة
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.write("كن حذرًا دائمًا، ولا تشارك بياناتك الشخصية أو رموز التحقق.")
        else:
            st.warning("الرجاء إدخال رسالة أولاً.")
