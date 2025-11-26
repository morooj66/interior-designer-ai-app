import os
import json
import textwrap
import streamlit as st
from openai import OpenAI

# -------- إعداد الـ OpenAI Client --------
def get_client():
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not api_key:
st.error(" لم يتم العثور على مفتاح OpenAI. أضيفيه في Secrets في Streamlit Cloud.")
st.stop()
return OpenAI(api_key=api_key)

client = get_client()

# -------- دوال مساعدة لاستدعاء النموذج --------
def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.6) -> str:
response = client.chat.completions.create(
model="gpt-4o-mini",
temperature=temperature,
messages=[
{"role": "system", "content": system_prompt},
{"role": "user", "content": user_prompt},
],
)
return response.choices[0].message.content


# -------- إيـچـنـت 1: مهندس ديكور ومعماري --------
def interior_designer_agent(description: str, style: str, budget: int, language: str = "ar") -> dict:
system_prompt = """
You are a world-class interior designer AND architect.
You design realistic, buildable interiors for bedrooms and living rooms,
with excellent sense of color, lighting, layout, and function.

You MUST return a compact JSON object with the following structure:

{
"overview": "short paragraph",
"style_direction": "short paragraph",
"color_palette": [
{ "name": "Warm Beige", "hex": "#E9DDCF", "usage": "Walls & large areas" }
],
"layout_tips": [
"tip 1",
"tip 2"
],
"lighting_plan": [
"tip 1",
"tip 2"
],
"mistakes_to_avoid": [
"mistake 1",
"mistake 2"
],
"pinterest_moodboard": [
"keyword 1",
"keyword 2",
"keyword 3"
]
}

Do NOT add any extra keys.
Respond ONLY with valid JSON – no markdown, no explanations.
Language of all text should match the user language (Arabic if user text is Arabic).
""".strip()

user_prompt = f"""
Room description:
{description}

Preferred style: {style}
Budget: {budget} SAR (approx)

Language: {language}
""".strip()

raw = call_llm(system_prompt, user_prompt)
try:
data = json.loads(raw)
except json.JSONDecodeError:
# في حال النموذج لخبط، نحطه كنص فقط
data = {
"overview": raw,
"style_direction": "",
"color_palette": [],
"layout_tips": [],
"lighting_plan": [],
"mistakes_to_avoid": [],
"pinterest_moodboard": [],
}
return data


# -------- إيـچـنـت 2: خبير أثاث --------
def furniture_agent(style: str, budget: int, language: str = "ar") -> dict:
system_prompt = """
You are a senior furniture expert and stylist.
You choose realistic furniture pieces that can be found in common furniture stores
(IKEA, Home Center, Pottery Barn, local brands, etc.).

Return STRICT JSON with this structure:

{
"recommended_furniture": [
{
"name": "Beige L-shaped Sofa",
"category": "Sofa",
"price_level": "medium", // low, medium, high
"estimated_price_sar": 3500,
"why": "reason",
"placement_tip": "where and how to place it",
"style_match": "how it fits the style"
}
]
}

No extra keys. No markdown. Text language must match user language.
""".strip()

user_prompt = f"""
Target style: {style}
Budget: {budget} SAR
Language: {language}

Give pieces that feel like Pinterest / modern real apartments in the Gulf region.
""".strip()

raw = call_llm(system_prompt, user_prompt)
try:
data = json.loads(raw)
except json.JSONDecodeError:
data = {
"recommended_furniture": [
{
"name": "Modern sofa",
"category": "Sofa",
"price_level": "medium",
"estimated_price_sar": budget // 3 if budget else 0,
"why": raw[:200],
"placement_tip": "",
"style_match": "",
}
]
}
return data


# -------- دالة تجمع النتائج من الإيچنتين --------
def run_design_system(description: str, style: str, budget: int, language: str = "ar") -> dict:
design = interior_designer_agent(description, style, budget, language)
furniture = furniture_agent(style, budget, language)
return {
"design": design,
"furniture": furniture,
}


# -------- إعداد صفحة Streamlit --------
st.set_page_config(
page_title="AI Interior Design Studio",
page_icon="🛋️",
layout="wide",
)

# -------- الهيدر الفخم --------
with st.container():
col1, col2 = st.columns([2, 1])
with col1:
st.markdown(
"""
<h1 style="font-family: 'Georgia', serif; font-size: 42px; margin-bottom: 0;">
AI Interior Design Studio
</h1>
<p style="font-size: 16px; opacity: 0.8;">
مساعد تصميم داخلي ذكي يجمع بين مهندس ديكور، مهندس معماري، وخبير أثاث — يعطيك خطة متكاملة كأنك طلبتي استشارة فاخرة أونلاين.
</p>
""",
unsafe_allow_html=True,
)
with col2:
st.markdown(
"""
<div style="background: #1f1f1f; padding: 12px 16px; border-radius: 16px; text-align: right;">
<p style="margin:0; font-size: 13px; opacity:0.9;">by Murooj · Interior AI Assistant</p>
</div>
""",
unsafe_allow_html=True,
)

st.markdown("---")

# -------- نموذج الإدخال --------
left, right = st.columns([1.6, 1.2])

with left:
st.subheader("📝 وصف الغرفة", anchor=False)
description = st.text_area(
"اكتبي وصف الغرفة (المساحة، الإحساس، الألوان المفضلة، الاستخدام...)",
value="غرفة نوم مريحة بدرجات البيج، أجواء هادئة، طابع فندقي بسيط وفخم...",
height=140,
)

style = st.selectbox(
"اختاري النمط",
options=[
"Luxury",
"Modern",
"Minimal",
"Japandi",
"Scandinavian",
"Classic",
"Boho Chic",
],
index=1,
)

budget = st.slider(
"الميزانية التقريبية (ريال سعودي)",
min_value=1000,
max_value=30000,
step=1000,
value=8000,
)

language = st.radio(
"Language / اللغة",
options=["ar", "en"],
format_func=lambda x: "العربية" if x == "ar" else "English",
horizontal=True,
)

generate_btn = st.button("✨ حلّل التصميم وأعطني الخطة", use_container_width=True)

with right:
st.subheader("💡 كيف يشتغل المساعد؟", anchor=False)
st.markdown(
"""
- يقرأ وصف الغرفة والنمط والميزانية
- إيچنت 1: مهندس ديكور + معماري يعطيك:
- رؤية عامة، اتجاه التصميم
- باليت ألوان احترافية
- خطة إضاءة، توزيع، وأخطاء تتجنبينها
- إيچنت 2: خبير أثاث:
- يقترح قطع أثاث حقيقية بالميزانية
- أين توضع؟ ولماذا تناسب أسلوبك؟

كل النتايج مبنية على نموذج GPT-4o-mini من OpenAI ✨
""",
unsafe_allow_html=True,
)

st.markdown("---")

# -------- تنفيذ التحليل وعرض النتائج --------
if generate_btn:
if not description.strip():
st.warning("اكتبي وصف للغرفة أولاً 🤍")
else:
with st.spinner("جاري تحليل الغرفة وتصميم خطة فخمة لك..."):
result = run_design_system(description, style, budget, language)

design = result.get("design", {})
furniture = result.get("furniture", {})

tabs = st.tabs(
[
"🎯 Overview",
"🎨 Color Palette",
"📐 Layout & Flow",
"💡 Lighting Plan",
"🛋️ Furniture Picks",
"⚠️ Mistakes to Avoid",
"📌 Pinterest Moodboard",
]
)

# --- Overview ---
with tabs[0]:
st.subheader("نظرة عامة على التصميم", anchor=False)
st.write(design.get("overview", ""))
if design.get("style_direction"):
st.markdown("#### اتجاه التصميم")
st.write(design.get("style_direction", ""))

# --- Color Palette ---
with tabs[1]:
st.subheader("باليت الألوان", anchor=False)
palette = design.get("color_palette", [])
if not palette:
st.write("لا توجد تفاصيل ألوان كافية، أعيدي المحاولة بوصف أدق.")
else:
cols = st.columns(len(palette))
for i, color in enumerate(palette):
with cols[i]:
hex_code = color.get("hex", "#CCCCCC")
st.markdown(
f"""
<div style="border-radius: 12px; overflow: hidden; border: 1px solid #333;">
<div style="height: 60px; background:{hex_code};"></div>
<div style="padding: 6px 8px; font-size: 11px;">
<b>{color.get('name','')}</b><br/>
<code>{hex_code}</code><br/>
<span style="opacity:0.8;">{color.get('usage','')}</span>
</div>
</div>
""",
unsafe_allow_html=True,
)

# --- Layout ---
with tabs[2]:
st.subheader("توزيع الأثاث والحركة", anchor=False)
tips = design.get("layout_tips", [])
if tips:
for t in tips:
st.markdown(f"- {t}")
else:
st.write("لا توجد نصائح توزيع كافية.")

# --- Lighting ---
with tabs[3]:
st.subheader("خطة الإضاءة", anchor=False)
lighting = design.get("lighting_plan", [])
if lighting:
for l in lighting:
st.markdown(f"- {l}")
else:
st.write("لا توجد خطة إضاءة كافية.")

# --- Furniture ---
with tabs[4]:
st.subheader("اقتراحات الأثاث حسب الميزانية", anchor=False)
items = furniture.get("recommended_furniture", [])
if not items:
st.write("لا توجد اقتراحات أثاث، حاولي مرة أخرى بوصف أوضح.")
else:
for item in items:
with st.container():
st.markdown(
f"""
<div style="border-radius: 16px; border:1px solid #333; padding:12px 14px; margin-bottom:10px;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<b>{item.get('name','قطعة أثاث')}</b>
<span style="opacity:0.7; font-size:12px;"> · {item.get('category','')}</span>
</div>
<div style="font-size:12px; opacity:0.8;">
{item.get('price_level','')} · ~{item.get('estimated_price_sar',0)} SAR
</div>
</div>
<div style="margin-top:6px; font-size:13px;">
<b>لماذا؟</b> {item.get('why','')}
</div>
<div style="margin-top:4px; font-size:12px; opacity:0.9;">
<b>مكانها المثالي:</b> {item.get('placement_tip','')}
</div>
<div style="margin-top:4px; font-size:12px; opacity:0.9;">
<b>تناسقها مع الأسلوب:</b> {item.get('style_match','')}
</div>
</div>
""",
unsafe_allow_html=True,
)

# --- Mistakes ---
with tabs[5]:
st.subheader("أخطاء تجنّبيها", anchor=False)
mistakes = design.get("mistakes_to_avoid", [])
if mistakes:
for m in mistakes:
st.markdown(f"- {m}")
else:
st.write("لا توجد قائمة أخطاء، حاولي سؤال المساعد عن الأخطاء بشكل صريح في الوصف.")

# --- Moodboard Keywords ---
with tabs[6]:
st.subheader("كلمات مفتاحية لمودبورد Pinterest", anchor=False)
tags = design.get("pinterest_moodboard", [])
if tags:
st.markdown(
"استخدمي هذه الكلمات في بحث Pinterest / Midjourney / أي أداة صور:"
)
st.markdown(
" ".join([f"`{t}`" for t in tags])
)
else:
st.write("لا توجد كلمات مودبورد، جرّبي أن تطلبي Moodboard في وصف الغرفة.")
