import streamlit as st
import re
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import io
import base64

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

# التبويبات
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📩 فحص الرسائل",
    "🔗 فحص الروابط",
    "🖼️ فحص الصور",
    "📱 محاكاة SMS",
    "🛡️ الفحص الشامل"
])
# عنوان التطبيق
st.title("تطبيق أمان")
st.write("أهلاً بك! إما أن تضغط على زر المايك وتتحدث، أو تكتب الرسالة في المربع.")

# 1. زر التسجيل الصوتي
audio_bytes = audio_recorder(text="اضغط على المايك وتحدث", recording_color="#e83e2a", neutral_color="#ffffff", icon_size="2x")

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
    message_text = st.text_area("أو اكتب الرسالة هنا:", value=message, height=100)
    if message_text:
        message = message_text
    # 3. زر التحليل
    if st.button("تحليل الرسالة", use_container_width=True):
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

                if any(ext in url.lower() for ext in suspicious_extensions):
                    score += 2
                    reasons.append("وجود نطاق يستحق التحقق منه")

        
        # إعطاء النتيجة
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
