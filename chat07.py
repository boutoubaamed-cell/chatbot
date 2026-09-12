import os
import base64
from io import BytesIO
from google import genai
from google.genai import types
from gtts import gTTS
import docx
import pypdf
import streamlit as st

st.set_page_config(
    page_title="المساعد الذكي للمحاضرات الجامعية", page_icon="🎓", layout="wide"
)

# ---------------------------------------------------------
# تصميم وتنسيق CSS (ثابت ومستقر)
# ---------------------------------------------------------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
    background-color: #f1f5f9;
}

.main-header-wrapper {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 30px;
    box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.15);
    margin-bottom: 2.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.badge-pill {
    background-color: rgba(59, 130, 246, 0.25);
    color: #93c5fd;
    padding: 0.5rem 1.5rem;
    border-radius: 50px;
    font-size: 1.2rem;
    font-weight: 800;
    display: inline-block;
    margin-bottom: 1rem;
    border: 1px solid rgba(147, 197, 253, 0.3);
}

.header-text-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center; 
    justify-content: center;
    text-align: center; 
    min-width: 300px;
}

.header-text-section h1 {
    font-size: 2.3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    color: #ffffff !important;
    line-height: 1.3;
    text-align: center;
}

.header-sub {
    font-size: 1.25rem;
    font-weight: 600;
    color: #cbd5e1;
    margin: 0;
    text-align: center; 
}

.header-image-section {
    flex: 0 0 auto;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
}

[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-left: 1px solid #e2e8f0;
    padding-top: 1.5rem;
    box-shadow: 5px 0 25px rgba(0, 0, 0, 0.02);
}

.stButton>button {
    width: 100%;
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    color: white;
    border: none;
    padding: 0.7rem 1.2rem;
    border-radius: 12px;
    font-weight: 700;
    font-family: 'Cairo', sans-serif;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    opacity: 0.92;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);
}

button[kind="primary"] {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: white !important;
    font-size: 1.5rem !important;
    padding: 1.2rem 2rem !important;
    border-radius: 50px !important;
    border: none !important;
    box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3) !important;
    animation: pulse-btn 2s infinite !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}
button[kind="primary"]:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 15px 30px rgba(16, 185, 129, 0.5) !important;
}
@keyframes pulse-btn {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5); }
    70% { box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.stTextInput input, .stTextArea textarea, .stChatInput input {
    direction: rtl;
    text-align: right;
    border-radius: 12px !important;
    border: 1.5px solid #cbd5e1 !important;
    font-family: 'Cairo', sans-serif !important;
    background-color: #ffffff !important;
}

.stChatMessage {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    border: 1px solid #e2e8f0;
}

.footer-box {
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    padding: 1.8rem;
    border-radius: 16px;
    text-align: center;
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.9;
    margin-top: 4rem;
}
</style>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# معالجة الصورة
# ---------------------------------------------------------
img_html = '<div style="font-size: 90px; text-shadow: 0px 8px 20px rgba(0,0,0,0.3);">🤖</div>'
image_found = False

possible_paths = [
    r"C:\Users\Dell\PyCharmMiscProject\Ai Robot Vector Art.gif",
    r"C:\Users\Dell\PyCharmMiscProject\Ai Robot Vector Art.jpg",
    "Ai Robot Vector Art.gif",
    "Ai Robot Vector Art.jpg"
]

for path in possible_paths:
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                file_bytes = f.read()
                encoded_img = base64.b64encode(file_bytes).decode("utf-8")
                mime_type = "image/gif" if file_bytes.startswith(b'GIF') else "image/jpeg"

                img_html = f'<img src="data:{mime_type};base64,{encoded_img}" style="width: 150px; height: auto; object-fit: contain; mix-blend-mode: screen; filter: drop-shadow(0px 10px 25px rgba(0,0,0,0.4));">'
                image_found = True
                break
        except Exception:
            pass

if not image_found:
    st.error(r"⚠️ تنبيه: لم يتم العثور على ملف الصورة.")

# ---------------------------------------------------------
# الترويسة العليا
# ---------------------------------------------------------
header_html = f"""<div class="main-header-wrapper">
<div class="header-text-section">
<span class="badge-pill">✨ منصة التفاعل الأكاديمي الذكي</span>
<h1 style="color: white; font-family: 'Cairo', sans-serif;">مساعد الذكاء الاصطناعي التفاعلي للمحاضرات</h1>
<div class="header-sub">ChatBot * Lecture</div>
</div>
<div class="header-image-section">
{img_html}
</div>
</div>"""

st.markdown(header_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# الشريط الجانبي
# ---------------------------------------------------------

# 1. العنوان الرئيسي في المنتصف
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h2 style="color: #1e3a8a; font-weight: 800; font-family: 'Cairo', sans-serif; font-size: 1.6rem; margin-bottom: 5px;">منصة التفاعل الأكاديمي الذكي</h2>
        <div style="width: 40px; height: 4px; background-color: #2563eb; margin: 0 auto; border-radius: 5px;"></div>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. الرابط في المنتصف
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 15px;">
        <a href="https://aistudio.google.com/" target="_blank" style="text-decoration: none; color: #2563eb; font-weight: bold; font-size: 14px;">
            🔗 احصل على مفتاح مجاني من هنا
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)

# تم تصحيح الخطأ البرمجي هنا (فصل المتغير في سطر جديد)
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API Key:", type="password")

input_method = st.sidebar.radio("طريقة إدخال المحاضرة:", ["نسخ ولصق النص", "رفع ملف (PDF, Word, TXT)"])
lecture_text = ""

if input_method == "نسخ ولصق النص":
    lecture_text = st.sidebar.text_area("الصق نص المحاضرة هنا:", height=150)
else:
    uploaded_file = st.sidebar.file_uploader("اختر ملف المحاضرة", type=["pdf", "docx", "txt", "md"])
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        try:
            if file_extension in ["txt", "md"]:
                lecture_text = uploaded_file.read().decode("utf-8")
            elif file_extension == "pdf":
                reader = pypdf.PdfReader(uploaded_file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted: lecture_text += extracted + "\n"
            elif file_extension == "docx":
                doc = docx.Document(uploaded_file)
                lecture_text = "\n".join([para.text for para in doc.paragraphs])

            if lecture_text.strip():
                st.sidebar.success(f"تم استخراج المحتوى بنجاح!")
            else:
                st.sidebar.warning("الملف فارغ أو تعذر استخراج النص.")
        except Exception as e:
            st.sidebar.error(f"حدث خطأ أثناء قراءة الملف: {e}")

st.sidebar.markdown("---")

# 3. العناوين من أقصى اليمين باستخدام HTML لضمان المحاذاة المطلقة
st.sidebar.markdown(
    '<h3 style="text-align: right; color: #1e3a8a; font-family: \'Cairo\', sans-serif; margin-bottom: 10px;">⚙️ إعدادات</h3>', 
    unsafe_allow_html=True
)
voice_output_enabled = st.sidebar.checkbox("تفعيل الرد الصوتي للإجابات", value=True)

st.sidebar.markdown("---")

# عنوان "تواصل معنا" من أقصى اليمين
st.sidebar.markdown(
    '<h3 style="text-align: right; color: #1e3a8a; font-family: \'Cairo\', sans-serif; margin-bottom: 10px;">📬 تواصل معنا</h3>', 
    unsafe_allow_html=True
)

# نص "لأي استفسار" والإيميل في المنتصف بشكل أنيق
st.sidebar.markdown(
    """
    <div style="text-align: center; font-family: 'Cairo', sans-serif; font-size: 14px;">
        لأي استفسار أو دعم فني:<br>
        <a href="mailto:boutoubaamed@gmail.com" style="text-decoration: none; font-weight: bold; color: #2563eb; font-size: 15px;">boutoubaamed@gmail.com</a>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# واجهة الشات وتفعيل النموذج المستقر (3.6)
# ---------------------------------------------------------
if st.session_state.get("chat_active", False):
    st.markdown("---")
    st.subheader("💬 نافذة النقاش الطلابي")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "audio_bytes" in message and message["audio_bytes"]:
                st.audio(message["audio_bytes"], format="audio/mp3")

    st.markdown("##### 🎙️ الإملاء الصوتي (بديل الكتابة)")
    audio_value = st.audio_input("انقر لتسجيل سؤالك صوتياً:")
    text_prompt = st.chat_input("أو اطرح سؤالك أو استفسارك حول المحاضرة...")
    prompt = None

    if audio_value is not None:
        with st.spinner("جاري المعالجة..."):
            try:
                audio_bytes = audio_value.read()
                # تم إعادة النموذج إلى المستقر 3.6-flash هنا
                transcription_response = st.session_state.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        "قم بتحويل هذا التسجيل الصوتي بدقة إلى نص باللغة العربية واكتب السؤال مباشرة:",
                        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    ],
                )
                prompt = transcription_response.text
            except Exception as e:
                st.error(f"خطأ في التسجيل الصوتي: {e}")
    elif text_prompt:
        prompt = text_prompt

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جاري تحليل السؤال..."):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    bot_reply = response.text
                    st.markdown(bot_reply)

                    response_audio_bytes = None
                    if voice_output_enabled:
                        tts = gTTS(text=bot_reply, lang="ar", slow=False)
                        fp = BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        response_audio_bytes = fp.read()
                        st.audio(response_audio_bytes, format="audio/mp3", autoplay=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_reply,
                        "audio_bytes": response_audio_bytes,
                    })
                except Exception as e:
                    st.error(f"خطأ في الاتصال: {e}")
else:
    st.info("📌 أدخل مفتاح الـ API ومحتوى المحاضرة في الشريط الجانبي لفتح نافذة المحادثة.")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_button = st.button("🚀 بدء جلسة الشات التفاعلية للطلبة", type="primary", use_container_width=True)

    if start_button:
        if not api_key:
            st.error("⚠️ الرجاء إدخال مفتاح Gemini API Key في الشريط الجانبي أولاً.")
        elif not lecture_text.strip():
            st.error("⚠️ الرجاء إدخال أو رفع محتوى المحاضرة في الشريط الجانبي أولاً.")
        else:
            try:
                st.session_state.client = genai.Client(api_key=api_key)
                system_instruction = f"""أنت مساعد أكاديمي ذكي وصبور لطلبة الجامعة. 
مهمتك الأساسية هي الإجابة على استفسارات الطلبة وأسئلتهم بناءً على محتوى المحاضرة أدناه فقط. 
إذا كان السؤال خارج نطاق المحاضرة، اعتذر بلطف ووجه الطالب للتركيز على المادة العلمية للمحاضرة.

محتوى المحاضرة الرسمية:
{lecture_text}"""

                # تم إعادة النموذج إلى المستقر 3.6-flash هنا أيضاً
                st.session_state.chat = st.session_state.client.chats.create(
                    model="gemini-3.6-flash",
                    config=types.GenerateContentConfig(system_instruction=system_instruction)
                )
                st.session_state.chat_active = True
                st.rerun()
            except Exception as e:
                st.error(f"خطأ في تهيئة الاتصال: {e}")

# ---------------------------------------------------------
# التذييل
# ---------------------------------------------------------
footer_html = """<div class="footer-box">
إصدار تجريبي © 2026 ® جميع الحقوق محفوظة<br>
<span style="font-family: Arial, sans-serif; font-weight: bold; color: #1e3a8a;">Developed by Pr. Mohamed Boutouba</span><br>
جامعة عين تموشنت ® الجزائر
</div>"""

st.markdown(footer_html, unsafe_allow_html=True)
