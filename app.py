import streamlit as st
import google.generativeai as genai
import base64
import pathlib

# 1. إعداد الصفحة
st.set_page_config(
    page_title="دال التقنية | مهندس الأوامر", 
    page_icon="⟡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تهيئة CSS
def load_css(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("لم يتم العثور على ملف style.css")

load_css("style.css")

# 3. دوال مساعدة (شعار دال التقنية) - تم التعديل للاسم الدقيق للملف
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

# استخدمنا الاسم المطابق تماماً للملف المرفق
logo_base64 = get_base64_of_bin_file("شعار دال التقنية.png")

# 4. الترويسة الرئيسية (Header)
if logo_base64:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: flex-start; gap: 15px; margin-bottom: 20px; direction: rtl;">
            <img src="data:image/png;base64,{logo_base64}" alt="Daal Tech Logo" style="height: 65px; border-radius: 8px;">
            <div>
                <h1 style="margin: 0; color: #0F4C81;">مهندس الأوامر الذكي</h1>
                <p style="margin: 5px 0 0 0; color: #5F6368; font-size: 0.95rem;">
                AI | DIGITAL TRANSFORMATION | SMART SOLUTIONS
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown('<h1 style="color: #0F4C81;">⟡ دال التقنية | مهندس الأوامر الذكي</h1>', unsafe_allow_html=True)

st.markdown("<p style='color: #5F6368; font-size: 1.1rem;'>✦ أدخل وصفاً مختصراً لطلبك، وسنعمل على بناء Prompt احترافي مخصص لدعم ابتكاراتك.</p>", unsafe_allow_html=True)
st.markdown("---")

# 5. إدارة ذاكرة التطبيق
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_prompts" not in st.session_state:
    st.session_state.saved_prompts = []

# 6. الشريط الجانبي (Sidebar)
with st.sidebar:
    st.markdown("<h2 style='color: #0F4C81;'>⛭ الإعدادات والمكتبة</h2>", unsafe_allow_html=True)
    
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("🔑 أدخل مفتاح Gemini API الخاص بك:", type="password")
        
    st.markdown("---")
    
    st.markdown("### ◫ مكتبة الأوامر المحفوظة")
    if not st.session_state.saved_prompts:
        st.markdown("<p style='color: #8b949e; font-size: 0.9em;'>لا توجد أوامر محفوظة حالياً.</p>", unsafe_allow_html=True)
    else:
        for idx, saved_item in enumerate(reversed(st.session_state.saved_prompts)):
            with st.expander(f"⎔ {saved_item['title']}", expanded=False):
                st.markdown(f"""**الأمر بالإنجليزية:**\n```text\n{saved_item['prompt']}\n
```""")
                st.markdown(f"**الوصف:** {saved_item['title']}")

if not api_key:
    st.warning("⚠️ يرجى إدخال مفتاح API في الشريط الجانبي للبدء.")
    st.stop()

# 7. تهيئة النموذج
genai.configure(api_key=api_key)

system_instruction = """
You are an Expert Prompt Engineer for 'Dal Technology'. Your goal is to help the user craft the most effective, highly detailed, and professional prompt for any AI model based on their brief description.

Workflow:
1. Analyze the User's Input.
2. Evaluate Completeness: If the request lacks crucial context, ask 1 to 3 concise questions in Arabic to gather missing information. DO NOT generate the final prompt yet.
3. Generate the Final Prompt: Once you have enough context, construct a Master Prompt in ENGLISH.
4. Format the Output:
   - A brief encouraging sentence in Arabic.
   - The English Prompt inside a code block.
   - An accurate Arabic translation of the prompt below the code block.

Tone: Professional, high-tech, futuristic, helpful, and concise. Language: Arabic for chat/translation, English for the final prompt.
"""

@st.cache_resource(show_spinner=False)
def load_model(_api_key):
    return genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        system_instruction=system_instruction
    )

model = load_model(api_key)

if st.session_state.chat_session is None:
    st.session_state.chat_session = model.start_chat(history=[])

# تهيئة متغيرات الحفظ في الذاكرة (أضف هذا إذا لم يكن موجوداً أعلى الملف مع بقية الـ Session States)
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# 8. واجهة المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── زر الحفظ (تمت إزالة الأعمدة لمنع انضغاط النص) ──
if st.session_state.last_response:
    if st.button("✦ حفظ الأمر الأخير في المكتبة", key="save_current_prompt"):
        st.session_state.saved_prompts.append({
            "title": st.session_state.last_prompt[:40] + "..." if len(st.session_state.last_prompt) > 40 else st.session_state.last_prompt,
            "prompt": st.session_state.last_response
        })
        st.session_state.last_response = None 
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True) # مسافة جمالية بسيطة

# ── زر المرفقات (تمت إزالة الأعمدة وإعادته لوضعه الطبيعي المريح) ──
with st.expander("📎 إرفاق ملف أو مستند لدعم الأمر (اختياري)", expanded=False):
    uploaded_file = st.file_uploader("", type=["txt", "pdf", "docx"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"تم إرفاق الملف: {uploaded_file.name} بنجاح!")

# ── مربع الإدخال الرئيسي ──
if user_prompt := st.chat_input("اكتب فكرتك هنا (مثال: أريد بناء نظام ذكاء اصطناعي للموارد البشرية)..."):
    
    st.session_state.last_prompt = user_prompt
    
    final_prompt = user_prompt
    if 'uploaded_file' in locals() and uploaded_file is not None:
        final_prompt += f"\n\n[ملاحظة: قام المستخدم بإرفاق ملف باسم {uploaded_file.name}]"
        
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("جاري التحليل المعماري للأمر..."):
            try:
                response = st.session_state.chat_session.send_message(final_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                st.session_state.last_response = response.text
                st.rerun() 

            except Exception as e:
                st.error(f"حدث خطأ في الاتصال. التفاصيل: {e}")