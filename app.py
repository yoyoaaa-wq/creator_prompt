import streamlit as st
import google.generativeai as genai
import anthropic
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
        pass

load_css("style.css")

# 3. دوال مساعدة (شعار دال التقنية)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

logo_base64 = get_base64_of_bin_file("شعار دال التقنية.png")

# 4. الترويسة الرئيسية
if logo_base64:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: flex-start; gap: 15px; margin-bottom: 20px; direction: rtl;">
            <img src="data:image/png;base64,{logo_base64}" alt="Daal Tech Logo" style="height: 65px; border-radius: 8px;">
            <div>
                <h1 style="margin: 0; color: #0F4C81;">مهندس الأوامر الذكي <span style="font-size:0.5em; color:#00C8FF;">(Gemini + Claude Hybrid)</span></h1>
                <p style="margin: 5px 0 0 0; color: #5F6368; font-size: 0.95rem;">
                AI | DIGITAL TRANSFORMATION | SMART SOLUTIONS
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown('<h1 style="color: #0F4C81;">⟡ دال التقنية | مهندس الأوامر (Hybrid)</h1>', unsafe_allow_html=True)

st.markdown("---")

# 5. إدارة ذاكرة التطبيق (تهيئة الذاكرة المزدوجة للنموذجين)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "saved_prompts" not in st.session_state:
    st.session_state.saved_prompts = []
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# 6. الشريط الجانبي (مفاتيح API والمكتبة)
with st.sidebar:
    st.markdown("<h2 style='color: #0F4C81;'>⛭ الإعدادات والمكتبة</h2>", unsafe_allow_html=True)
    
    gemini_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("🔑 مفتاح Gemini API:", type="password")
    claude_key = st.secrets.get("ANTHROPIC_API_KEY") or st.text_input("🔑 مفتاح Claude API:", type="password")
        
    st.markdown("---")
    
    st.markdown("### ◫ مكتبة الأوامر المحفوظة")
    if not st.session_state.saved_prompts:
        st.markdown("<p style='color: #8b949e; font-size: 0.9em;'>لا توجد أوامر محفوظة حالياً.</p>", unsafe_allow_html=True)
    else:
        for idx, saved_item in enumerate(reversed(st.session_state.saved_prompts)):
            with st.expander(f"⎔ {saved_item['title']}", expanded=False):
                st.markdown(f"""**الأمر:**\n```text\n{saved_item['prompt']}\n```""")

if not gemini_key or not claude_key:
    st.warning("⚠️ يرجى التأكد من توفر مفاتيح API لكل من Gemini و Claude للبدء.")
    st.stop()

# 7. تهيئة النماذج (Gemini و Claude)
genai.configure(api_key=gemini_key)
claude_client = anthropic.Anthropic(api_key=claude_key)

# تعليمات Claude كمهندس أوركسترا (Orchestrator)
claude_system = """
You are the Lead Prompt Engineer & Orchestrator for 'Dal Technology'.
You will receive the User's Request AND a preliminary analysis from your partner AI (Gemini).

Your Workflow:
1. Review the User's Request.
2. Review Gemini's ideas and analysis.
3. Merge your own advanced reasoning with Gemini's input.
4. Output Rules (Strict):
   - IF missing context: Ask 1-3 concise questions in Arabic. Merge your questions with Gemini's, DO NOT repeat, DO NOT contradict.
   - IF context is sufficient: Generate the ultimate Master Prompt in ENGLISH (inside a code block), combining the best of both models. Add an Arabic translation below it.
   - Speak directly to the user in a professional Arabic tone. Do not mention "Gemini said" or explain the merging process. Just deliver the final masterpiece.
"""

@st.cache_resource(show_spinner=False)
def load_gemini(_api_key):
    return genai.GenerativeModel(model_name="gemini-3.5-flash")

gemini_model = load_gemini(gemini_key)

# تهيئة جلسات المحادثة المنفصلة في الذاكرة
if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = gemini_model.start_chat(history=[])
if "claude_history" not in st.session_state:
    st.session_state.claude_history = []

# 8. واجهة المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# زر الحفظ
if st.session_state.last_response:
    if st.button("✦ حفظ الأمر الأخير في المكتبة", key="save_current_prompt"):
        st.session_state.saved_prompts.append({
            "title": st.session_state.last_prompt[:40] + "..." if len(st.session_state.last_prompt) > 40 else st.session_state.last_prompt,
            "prompt": st.session_state.last_response
        })
        st.session_state.last_response = None 
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 9. محرك الأوركسترا الهجين (الاستقبال والمعالجة)
if user_prompt := st.chat_input("اكتب فكرتك هنا (مثال: أريد بناء نظام ذكاء اصطناعي للموارد البشرية)..."):
    
    st.session_state.last_prompt = user_prompt
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("جاري المعالجة الهجينة (Gemini Brainstorming + Claude Orchestration)..."):
            try:
                # الخطوة 1: استدعاء Gemini للحصول على العصف الذهني المبدئي
                gemini_instruction = f"User Request: {user_prompt}\nProvide your analysis, draft prompt, or clarifying questions in Arabic."
                gemini_reply = st.session_state.gemini_chat.send_message(gemini_instruction).text

                # الخطوة 2: بناء أمر الهجين (Hybrid Prompt) وتمريره إلى Claude
                hybrid_prompt = f"""
                الطلب الأصلي للمستخدم:
                {user_prompt}

                تحليل وأفكار المحرك الأول (Gemini):
                {gemini_reply}

                المطلوب: قم بدورك كأوركسترا. ادمج الأفكار، امنع التكرار، وأصدر النتيجة النهائية مباشرة للمستخدم.
                """
                
                # إضافة الطلب لداكرة Claude
                st.session_state.claude_history.append({"role": "user", "content": hybrid_prompt})

                # الخطوة 3: استدعاء Claude لإصدار النتيجة النهائية المصفاة
                claude_response = claude_client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=3500,
                    system=claude_system,
                    messages=st.session_state.claude_history
                )
                
                final_answer = claude_response.content[0].text
                
                # حفظ الرد في ذاكرة Claude للاستمرار في السياق
                st.session_state.claude_history.append({"role": "assistant", "content": final_answer})

                # العرض والحفظ في الواجهة
                st.markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                st.session_state.last_response = final_answer
                st.rerun() 

            except Exception as e:
                st.error(f"حدث خطأ في الاتصال بمزودي الذكاء الاصطناعي. التفاصيل: {e}")