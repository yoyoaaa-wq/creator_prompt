# -*- coding: utf-8 -*-
"""
============================================================================
قالب جاهز: زر إخفاء / إظهار الشريط الجانبي (Sidebar Drawer Toggle) في Streamlit
============================================================================

الفكرة:
    يعيد تنسيق زر الطيّ الأصلي في Streamlit (stSidebarCollapsedControl) ليتحوّل
    الشريط الجانبي إلى لوحة منزلقة (drawer) على شاشات الجوال (<= 768px افتراضياً):
        - عند الطي  : ينزلق الشريط خارج الشاشة لليسار ويختفي.
        - عند الفتح : يظهر كطبقة علوية فوق المحتوى مع ظل جانبي.
        - الزر العائم أعلى اليسار يفتح الشريط، وزر الإغلاق داخل الشريط يطويه.

طريقة الاستخدام:
    from sidebar_toggle_template import inject_sidebar_toggle
    inject_sidebar_toggle()                       # بالقيم الافتراضية (زر ملوّن)
    inject_sidebar_toggle(btn_bg=None, btn_color=None)   # إبقاء اللون دون تغيير

ملاحظات:
    - btn_bg=None  -> لا يُغيّر لون خلفية الزر (يبقى الافتراضي).
    - btn_color=None -> لا يُغيّر لون أيقونة الزر.
    - يعتمد على زر الطيّ الأصلي، فلا حاجة لإدارة session_state إطلاقاً.
"""

import streamlit as st

# علامات نائبة (__...__) بدل f-string لتجنّب مشاكل الأقواس {} في CSS
_SIDEBAR_TOGGLE_CSS = """
<style>
@media screen and (max-width: __BREAKPOINT__px) {

    /* الشريط الجانبي — مخفي عند الطي (ينزلق خارج الشاشة لليسار) */
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
        visibility: hidden !important;
        transform: translateX(-110%) !important;
        transition: transform 0.28s ease !important;
    }

    /* الشريط الجانبي — طبقة علوية منزلقة عند الفتح */
    [data-testid="stSidebar"][aria-expanded="true"] {
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        height: 100vh !important;
        width: __DRAWER_W__ !important;
        max-width: __DRAWER_MAXW__ !important;
        z-index: 9999 !important;
        visibility: visible !important;
        transform: translateX(0) !important;
        transition: transform 0.28s ease !important;
        box-shadow: 6px 0 24px rgba(0,0,0,0.28) !important;
        overflow-y: auto !important;
    }

    /* حاوية زر فتح/إغلاق الشريط — تثبيتها أعلى اليسار */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 10px !important; left: 10px !important;
        z-index: 10000 !important;
        width: auto !important;
        background: transparent !important;
    }

__BTN_RULES__
}
</style>
"""


def inject_sidebar_toggle(
    breakpoint_px: int = 768,
    drawer_width: str = "78vw",
    drawer_max_width: str = "290px",
    btn_bg: str | None = "#0B4F47",
    btn_color: str | None = "#FFFFFF",
    btn_size_px: int = 38,
    btn_radius: str = "8px",
    btn_shadow: str = "0 2px 8px rgba(0,0,0,0.08)",
) -> None:
    """يحقن CSS لزر إخفاء/إظهار الشريط الجانبي كلوحة منزلقة على الجوال.

    مرّر btn_bg=None و/أو btn_color=None لإبقاء لون الزر دون تغيير (شكل فقط).
    """
    # بناء قاعدة الزر سطراً سطراً (لإتاحة تجاهل اللون عند الطلب)
    lines = ['    [data-testid="stSidebarCollapsedControl"] button {']
    if btn_bg:
        lines.append(f"        background: {btn_bg} !important;")
        lines.append("        background-image: none !important;")
    if btn_color:
        lines.append(f"        color: {btn_color} !important;")
    lines.append(f"        width: {btn_size_px}px !important;")
    lines.append(f"        height: {btn_size_px}px !important;")
    lines.append("        min-height: unset !important;")
    lines.append(f"        border-radius: {btn_radius} !important;")
    lines.append("        padding: 6px !important;")
    lines.append("        border: none !important;")
    lines.append(f"        box-shadow: {btn_shadow} !important;")
    lines.append("    }")
    if btn_color:
        lines.append(
            f'    [data-testid="stSidebarCollapsedControl"] button * {{ color: {btn_color} !important; }}'
        )
    btn_rules = "\n".join(lines)

    css = (
        _SIDEBAR_TOGGLE_CSS
        .replace("__BREAKPOINT__", str(breakpoint_px))
        .replace("__DRAWER_W__", drawer_width)
        .replace("__DRAWER_MAXW__", drawer_max_width)
        .replace("__BTN_RULES__", btn_rules)
    )
    st.markdown(css, unsafe_allow_html=True)


# مثال تشغيل مستقل للاختبار
if __name__ == "__main__":
    st.set_page_config(page_title="اختبار القالب", layout="wide",
                       initial_sidebar_state="auto")
    inject_sidebar_toggle()
    with st.sidebar:
        st.header("الشريط الجانبي")
        st.write("صغّر نافذة المتصفح إلى أقل من 768px لتجربة الوضع المنزلق.")
    st.title("القالب يعمل")
