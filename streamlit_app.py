import os

import base64

from io import BytesIO



import streamlit as st

from openai import OpenAI



# ========== إعداد مفتاح OpenAI ==========

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:

    st.set_page_config(page_title="AI Interior Studio", page_icon="🛋️", layout="wide")

    st.error("⚠️ ضيفي متغير البيئة OPENAI_API_KEY في Streamlit Secrets.")

    st.stop()



client = OpenAI(api_key=api_key)



# ========== إعداد الصفحة ==========

st.set_page_config(page_title="AI Interior Studio", page_icon="🛋️", layout="wide")



# ========== الشريط الجانبي ==========

with st.sidebar:

    st.title("🛋️ AI Interior Studio")

    st.caption("Multi-Agent Interior Assistant:")

    st.markdown(

        "- 🏛️ **Architect Agent** (المخطط والتوزيع)\n"

        "- 🪑 **Furniture Stylist** (اختيار الأثاث والميزانية)\n"

        "- 🎨 **Color Expert** (الألوان والخامات)"

    )

    st.markdown("---")

    st.markdown("Made by **Morooj** ✨")



# ========== تهيئة حالة الجلسة ==========

if "results" not in st.session_state:

    st.session_state["results"] = {

        "summary": None,

        "architect": None,

        "furniture": None,

        "colors": None,

        "description": "",

        "style": "",

        "purpose": "",

        "budget": 0,

    }



# ========== تقسيم الصفحة يمين/يسار ==========

left_col, right_col = st.columns([1, 2])



# ================= LEFT: إدخال بيانات الغرفة =================

with left_col:

    st.markdown("### 🧾 Room Details")



    description = st.text_area(

        "Room Description",

        placeholder="Example: Cozy living room 4x5m with one big window, wants luxury vibes with beige & brown tones...",

    )



    style = st.selectbox(

        "Preferred Style",

        ["Modern", "Minimal", "Classic", "Boho", "Luxury", "Japandi"],

        index=0,

    )



    purpose = st.text_input(

        "Purpose of the Room",

        value="Relaxing, watching TV, hosting guests...",

    )



    budget = st.number_input(

        "Budget (SAR)",

        min_value=1000,

        max_value=300000,

        value=15000,

        step=1000,

    )



    uploaded_photo = st.file_uploader(

        "Upload a reference photo (optional)",

        type=["jpg", "jpeg", "png"],

    )



    generate_moodboard = st.checkbox("Generate AI Moodboard + 3D Render", value=True)



    clicked = st.button("✨ Generate Full Interior Plan", use_container_width=True)





# ================= دالة الـ Agents (نص) =================

def call_agent(role_description: str, description: str, style: str, purpose: str, budget: int) -> str:

    """

    role_description مثال:

    'an architect and layout expert'

    """

    user_prompt = f"""

You are {role_description} for interior design.



Room description: {description}

Preferred style: {style}

Purpose: {purpose}

Budget: {budget} SAR



Provide a clear, structured plan in bullet points.

Be specific and practical, not generic.

"""



    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {

                "role": "system",

                "content": "You are a senior interior designer. Answer in clean Markdown with headings and bullet points.",

            },

            {"role": "user", "content": user_prompt},

        ],

        temperature=0.8,

    )



    return response.choices[0].message.content





# ================= دالة: بلوك المودبورد (أثاث + ألوان) =================

def render_moodboard_block(style: str, description: str, purpose: str, budget: int):

    """

    يعرض مودبورد مقسوم:

    - عمود يسار: قطع الأثاث

    - عمود يمين: الألوان والخامات

    وتحتها إضاءة مزاجية

    """

    col1, col2 = st.columns(2)



    # ----- 1) Furniture Pieces -----

    with col1:

        st.markdown("#### 🪑 Furniture Pieces")

        prompt_furniture = (

            f"Moodboard showing ONLY individual furniture pieces for a {style} room. "

            f"Room description: {description}. Purpose: {purpose}. Budget: {budget} SAR. "

            "Pinterest style, clean white background, no people, focus on items."

        )

        try:

            result = client.images.generate(

                model="gpt-image-1",

                prompt=prompt_furniture,

                size="1024x1024",

            )

            st.image(base64.b64decode(result.data[0].b64_json), use_column_width=True)

        except Exception as e:

            st.error(f"Furniture moodboard failed: {e}")



    # ----- 2) Colors + Materials -----

    with col2:

        st.markdown("#### 🎨 Color Palette & Materials")

        prompt_colors = (

            f"Color palette board + materials for a {style} interior. "

            f"Room description: {description}. Purpose: {purpose}. "

            "Show swatches, fabrics, wood, metal, stone, organized nicely."

        )

        try:

            result = client.images.generate(

                model="gpt-image-1",

                prompt=prompt_colors,

                size="1024x1024",

            )

            st.image(base64.b64decode(result.data[0].b64_json), use_column_width=True)

        except Exception as e:

            st.error(f"Color palette moodboard failed: {e}")



    # ----- 3) Lighting Mood -----

    st.markdown("#### 💡 Lighting Mood")

    prompt_lighting = (

        f"Lighting mood board for a {style} interior. Warm cozy cinematic lighting, "

        f"focus on lamps, wall lights, ceiling lights that match: {description}."

    )

    try:

        result = client.images.generate(

            model="gpt-image-1",

            prompt=prompt_lighting,

            size="1024x1024",

        )

        st.image(base64.b64decode(result.data[0].b64_json), use_column_width=True)

    except Exception as e:

        st.error(f"Lighting mood failed: {e}")





# ================= عند الضغط على الزر =================

if clicked:

    if not description.strip():

        st.warning("اكتبي وصف الغرفة أول 🙏")

    else:

        with st.spinner("✨ Agents are analyzing your space..."):



            architect_answer = call_agent(

                "an architect and layout expert",

                description,

                style,

                purpose,

                budget,

            )



            furniture_answer = call_agent(

                "a furniture selection and sourcing expert",

                description,

                style,

                purpose,

                budget,

            )



            color_answer = call_agent(

                "a color palette and materials specialist",

                description,

                style,

                purpose,

                budget,

            )



            summary_prompt = f"""

You are a senior interior designer.



Create a friendly summary (max 2 paragraphs + bullet list)

for this client based on:



Room: {description}

Style: {style}

Purpose: {purpose}

Budget: {budget} SAR



The summary should highlight:

- main layout idea

- key furniture choices

- key color palette and materials

            """



            summary_answer = client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[

                    {

                        "role": "system",

                        "content": "You summarize interior designs for non-technical clients in simple English.",

                    },

                    {"role": "user", "content": summary_prompt},

                ],

                temperature=0.7,

            ).choices[0].message.content



            # حفظ النتائج في session_state

            st.session_state["results"] = {

                "summary": summary_answer,

                "architect": architect_answer,

                "furniture": furniture_answer,

                "colors": color_answer,

                "description": description,

                "style": style,

                "purpose": purpose,

                "budget": budget,

            }



# ================= RIGHT: Tabs + Results =================

with right_col:

    st.markdown("### 📊 Design Analysis")



    tab_overview, tab_arch, tab_furn, tab_colors, tab_mood, tab_render = st.tabs(

        ["Overview", "Architect Plan", "Furniture Plan", "Color Palette", "AI Moodboard", "3D Render"]

    )



    results = st.session_state["results"]



    # ------ 1) Overview ------

    with tab_overview:

        if results["summary"]:

            st.markdown("### 🧾 Quick Summary")

            st.markdown(results["summary"])

        else:

            st.info("اضغطي **Generate Full Interior Plan** بعد تعبئة البيانات.")



    # ------ 2) Architect ------

    with tab_arch:

        if results["architect"]:

            st.markdown("### 🏛️ Architect / Layout Plan")

            st.markdown(results["architect"])

        else:

            st.info("سيظهر هنا مخطط توزيع الغرفة بعد تشغيل الأداة.")



    # ------ 3) Furniture ------

    with tab_furn:

        if results["furniture"]:

            st.markdown("### 🪑 Furniture & Budget Plan")

            st.markdown(results["furniture"])

        else:

            st.info("سيظهر هنا تحليل الأثاث بعد تشغيل الأداة.")



    # ------ 4) Colors ------

    with tab_colors:

        if results["colors"]:

            st.markdown("### 🎨 Color Palette & Materials")

            st.markdown(results["colors"])

        else:

            st.info("سيظهر هنا اقتراح الألوان والمواد بعد تشغيل الأداة.")



    # ------ 5) Moodboard ------

    with tab_mood:

        st.markdown("## 🎨 AI Moodboard")

        if generate_moodboard and results["description"]:

            render_moodboard_block(

                results["style"],

                results["description"],

                results["purpose"],

                results["budget"],

            )

        else:

            st.info("فعّلي خيار Generate AI Moodboard واعملي Generate.")



    # ------ 6) 3D Render ------

    with tab_render:

        st.markdown("## 🏡 3D Render")

        if results["description"]:

            prompt_3d = (

                f"Ultra realistic 3D render of a {results['style']} {results['purpose']} room, "

                f"budget {results['budget']} SAR. {results['description']}. "

                "Cinematic lighting, Pinterest style, no people, wide angle."

            )

            try:

                img_3d = client.images.generate(

                    model="gpt-image-1",

                    prompt=prompt_3d,

                    size="1024x1024",

                )

                st.image(base64.b64decode(img_3d.data[0].b64_json), use_column_width=True)

            except Exception as e:

                st.error(f"3D render failed: {e}")

        else:

            st.info("اكتبي وصف الغرفة ثم اضغطي Generate.")


