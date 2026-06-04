import streamlit as st
import google.generativeai as genai
import base64
import pathlib
import re
import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit.components.v1 as _components
from sidebar_toggle_template import inject_sidebar_toggle

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

# ── تطبيق قالب الشريط الجانبي المنزلق (Sidebar Drawer Toggle) ──
# btn_bg=None و btn_color=None لإبقاء لون زر الطي دون تغيير (تنسيق الشكل فقط)
inject_sidebar_toggle(btn_bg=None, btn_color=None)

# ── تنسيقات إضافية للجوال (غير متعلقة بالشريط الجانبي) ──
st.markdown(
    """
    <style>
    @media screen and (max-width: 768px) {
        [data-testid="block-container"] { padding: 0.8rem !important; }

        div[data-testid="stExpander"] [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 8px !important;
        }
        div[data-testid="stExpander"] [data-testid="stColumn"] {
            flex: 1 1 85px !important;
            min-width: 85px !important;
            max-width: 100% !important;
        }
        div[data-testid="stExpander"] .stButton > button {
            font-size: 13px !important;
            padding: 8px 6px !important;
            min-height: 36px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# ==========================================
# 3.1 دالة إرسال البرومبت عبر البريد
# ==========================================
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def send_prompt_email(to_email: str, prompt_text: str):
    """يرسل البرومبت (بالإنجليزية والعربية كما هو في رد المساعد) عبر Gmail SMTP.
    يعيد (نجاح: bool، رسالة: str)."""
    sender = st.secrets.get("EMAIL_SENDER")
    password = st.secrets.get("EMAIL_PASSWORD")
    if not sender or not password:
        return False, "لم يتم ضبط بيانات البريد (EMAIL_SENDER / EMAIL_PASSWORD) في secrets."

    safe = html.escape(prompt_text or "")
    body = f"""
    <div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;max-width:640px;margin:auto;padding:24px;border:1px solid #e6e6e6;border-radius:12px;background:#ffffff;">
        <h2 style="color:#0F4C81;text-align:center;margin:0 0 6px;">دال التقنية | مهندس الأوامر الذكي</h2>
        <p style="color:#5F6368;text-align:center;margin:0 0 18px;font-size:14px;">البرومبت الاحترافي (بالإنجليزية والعربية)</p>
        <div style="background:#f5f7fa;border:1px solid #e0e4ea;border-radius:10px;padding:16px;">
            <pre style="white-space:pre-wrap;word-wrap:break-word;font-family:Consolas,Menlo,monospace;font-size:13px;line-height:1.7;margin:0;text-align:left;direction:ltr;">{safe}</pre>
        </div>
        <p style="color:#9aa0a6;font-size:12px;text-align:center;margin-top:18px;">رسالة مُرسلة عبر تطبيق دال التقنية.</p>
    </div>
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = "البرومبت الاحترافي | دال التقنية"
        msg.attach(MIMEText(body, "html", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        return True, "تم إرسال البرومبت بنجاح."
    except Exception as e:
        return False, f"تعذّر الإرسال. التفاصيل: {e}"

# سكربت الإكمال التلقائي للبريد (يظهر فور كتابة @) — يُحقَن على حقل Streamlit الأصلي
_EMAIL_AUTOCOMPLETE_JS = """
<script>
(function(){
  const DOMAINS = ["gmail.com","hotmail.com","outlook.com","yahoo.com","icloud.com","live.com"];
  const doc = window.parent.document;
  function findInput(){
    return doc.querySelector('input[aria-label*="البريد"]') ||
           doc.querySelector('input[placeholder="name@example.com"]');
  }
  function setup(){
    const input = findInput();
    if(!input){ setTimeout(setup, 250); return; }
    if(input.dataset.acAttached === "1"){ return; }
    input.dataset.acAttached = "1";
    input.setAttribute("autocomplete","off");
    let dl = doc.getElementById("email_ac_list");
    if(!dl){ dl = doc.createElement("datalist"); dl.id = "email_ac_list"; doc.body.appendChild(dl); }
    input.setAttribute("list","email_ac_list");
    function refresh(){
      const v = input.value || "";
      dl.innerHTML = "";
      const at = v.indexOf("@");
      if(at === -1){ return; }
      const local = v.slice(0, at);
      const frag = v.slice(at+1).toLowerCase();
      DOMAINS.filter(function(d){ return d.indexOf(frag) === 0; })
             .forEach(function(d){
                const opt = doc.createElement("option");
                opt.value = local + "@" + d;
                dl.appendChild(opt);
             });
    }
    input.addEventListener("input", refresh);
    refresh();
  }
  setup();
})();
</script>
"""

# ==========================================
# 3.2 نافذة الإرسال عبر البريد (Modal Dialog)
# ==========================================
@st.dialog("✉ إرسال البرومبت عبر الإيميل")
def email_dialog(prompt_text: str):
    st.markdown(
        "<p style='color:#5F6368;font-size:0.92rem;'>أدخل بريد المستلم. بمجرد كتابة "
        "<b>@</b> ستظهر اقتراحات النطاقات تلقائياً.</p>",
        unsafe_allow_html=True
    )
    email = st.text_input("البريد الإلكتروني للمستلم", key="recipient_email",
                          placeholder="name@example.com")
    # حقن سكربت الإكمال التلقائي على الحقل أعلاه
    _components.html(_EMAIL_AUTOCOMPLETE_JS, height=0)

    c_send, c_cancel = st.columns(2)
    with c_send:
        if st.button("✦ إرسال", key="do_send_email", use_container_width=True, type="primary"):
            if not is_valid_email(email):
                st.error("يرجى إدخال بريد إلكتروني صحيح.")
            else:
                ok, msg = send_prompt_email(email.strip(), prompt_text)
                if ok:
                    st.session_state.open_email = False
                    st.session_state.email_feedback = ("success", msg)
                    st.rerun()
                else:
                    st.error(msg)
    with c_cancel:
        if st.button("إلغاء", key="cancel_email", use_container_width=True):
            st.session_state.open_email = False
            st.rerun()

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

# إشعار نتيجة الإرسال (يُعرض بعد إغلاق النافذة)
_fb = st.session_state.pop("email_feedback", None)
if _fb:
    if _fb[0] == "success":
        st.toast(_fb[1], icon="✅")
    else:
        st.toast(_fb[1], icon="⚠️")

# 8. واجهة المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── أزرار الإجراءات: حفظ في المكتبة + إرسال عبر الإيميل (جنباً إلى جنب) ──
if st.session_state.last_response:
    col_save, col_email = st.columns(2)

    with col_save:
        if st.button("✦ حفظ الأمر الأخير في المكتبة", key="save_current_prompt", use_container_width=True):
            st.session_state.saved_prompts.append({
                "title": st.session_state.last_prompt[:40] + "..." if len(st.session_state.last_prompt) > 40 else st.session_state.last_prompt,
                "prompt": st.session_state.last_response
            })
            st.session_state.last_response = None
            st.rerun()

    with col_email:
        if st.button("✉ إرسال عبر الإيميل", key="open_email_dialog", use_container_width=True):
            st.session_state.open_email = True

    # فتح النافذة المنبثقة عند الطلب (تبقى مفتوحة عبر إعادات التشغيل الداخلية)
    if st.session_state.get("open_email"):
        email_dialog(st.session_state.last_response)

st.markdown("<br>", unsafe_allow_html=True) # مسافة جمالية بسيطة

# ── مربع الإدخال الرئيسي ──
if user_prompt := st.chat_input("اكتب فكرتك هنا (مثال: أريد بناء نظام ذكاء اصطناعي للموارد البشرية)..."):
    
    st.session_state.last_prompt = user_prompt
    
    final_prompt = user_prompt
        
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
