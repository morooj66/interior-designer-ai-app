import os

import base64

from io import BytesIO



import streamlit as st

from openai import OpenAI

from PIL import Image



# ---------- OPENAI CLIENT ----------

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:

    st.set_page_config(page_title="AI Interior Studio", page_icon="🛋️", layout="wide")

    st.error("⚠️ Please set OPENAI_API_KEY in Streamlit Secrets.")

    st.stop()



client = OpenAI(api_key=api_key)



# ---------- PAGE CONFIG ----------

st.set_page_config(page_title="AI Interior Studio", page_icon="🛋️", layout="wide")



# ---------- SIDEBAR ----------

with st.sidebar:

    st.title("🛋️ AI Interior Studio")

    st.caption("Multi-agent interior assistant:")

    st.markdown("- 🏛️ **Architect agent**\n- 🪑 **Furniture stylist**\n- 🎨 **Color palette expert**")

    st.markdown("---")

    st.markdown("Made by **Morooj** ✨")



# ---------- INIT SESSION STATE ----------

if "results" not in st.session_state:

    st.session_state["results"] = {

        "summary": None,

        "architect": None,

        "furniture": None,

        "colors": None,

        "image_bytes": None,

    }


left_col, right_col = st.columns([1, 2])



with left_col:

    st.markdown("### 🧾 Room Details")



    description = st.text_area(

        "Room Description",

        placeholder="Example: Small bedroom 3x4m, one window, wants cozy modern vibes and a study corner...",

    )



    style = st.selectbox(

        "Preferred Style",

        ["Modern", "Minimal", "Classic", "Boho", "Luxury"],

        index=0,

    )



    purpose = st.text_input(

        "Purpose of the Room",

        value="Sleeping, studying, relaxing...",

    )



    budget = st.number_input(

        "Budget (SAR)",

        min_value=500,

        max_value=200000,

        value=5000,

        step=500,

    )



    st.markdown("### 🖼️ Optional: Room Photo")

    uploaded_photo = st.file_uploader(

        "Upload a reference photo (optional)",

        type=["jpg", "jpeg", "png"]

    )



    st.markdown("### 🎨 Optional: Generate AI Moodboard")

    generate_moodboard = st.checkbox(

        "Generate AI moodboard image for this design",

        value=True,

    )



    clicked = st.button("✨ Generate Full Interior Plan", use_container_width=True)



#------ OUTPUT TABS (This MUST be outside the columns) ------

tabs = st.tabs(["Overview", "Architect Plan", "Furniture Plan", "Color Palette", "AI Moodboard", "3D Render"])



with tabs[0]:

    st.markdown("## Overview")

    st.write(summary_answer)



with tabs[1]:

    st.markdown("## Architect Plan")

    st.write(architect_answer)



with tabs[2]:

    st.markdown("## Furniture Plan")

    st.write(furniture_answer)



with tabs[3]:

    st.markdown("## Color Palette")

    st.write(color_answer)



with tabs[4]:

    st.markdown("## AI Moodboard")

    if moodboard_img:

        st.image(moodboard_img, use_column_width=True)

    else:

        st.info("No moodboard generated.")



with tabs[5]:

    st.markdown("## 3D Render")

    if render_img:

        st.image(render_img, use_column_width=True)

    else:

        st.info("3D render not available.")


# ---------- HELPER: CALL CHAT AGENT ----------

def call_agent(role_description: str, description: str, style: str, purpose: str, budget: int) -> str:

    """

    role_description: مثل 'an architect and layout expert'

    يرجع نص من الموديل لهذا الدور.

    """

    user_prompt = f"""

You are {role_description} for interior design.



Room description: {description}

Preferred style: {style}

Purpose of the room: {purpose}

Budget: {budget} SAR



Give a clear, structured plan in bullet points. Be specific and practical.

"""



    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {

                "role": "system",

                "content": "You are a professional interior designer. Answer in clear Markdown with headings and bullet points.",

            },

            {"role": "user", "content": user_prompt},

        ],

        temperature=0.8,

    )



    return response.choices[0].message.content





# ---------- HELPER: GENERATE MOODBOARD IMAGE ----------
def generate_moodboard_image(description: str, style: str, purpose: str, budget: int, uploaded_photo):

    st.markdown("### 🎨 AI Moodboard (Furniture + Colors + Lighting + 3D Render)")



    try:

        # ======= 1) Furniture =======

        col1, col2 = st.columns(2)



        with col1:

            st.markdown("#### 🛋️ Furniture")

            furniture_img = client.images.generate(

                model="gpt-image-1",

                prompt=f"Moodboard showing furniture pieces for a {style} room. Room: {description}. Purpose: {purpose}. Budget: {budget} SAR.",

                size="1024x1024"

            )

            img_bytes = base64.b64decode(furniture_img.data[0].b64_json)

            st.image(img_bytes)



        # ======= 2) Color Palette =======

        with col2:

            st.markdown("#### 🎨 Colors")

            colors_img = client.images.generate(

                model="gpt-image-1",

                prompt=f"Color palette + materials for a {style} interior. Room: {description}. Purpose: {purpose}. Budget: {budget} SAR.",

                size="1024x1024"

            )

            img_bytes = base64.b64decode(colors_img.data[0].b64_json)

            st.image(img_bytes)



        # ======= 3) Lighting Mood =======

        st.markdown("#### 💡 Lighting Mood")

        lighting_img = client.images.generate(

            model="gpt-image-1",

            prompt=f"Lighting mood, warm cozy cinematic lighting for {style} interior.",

            size="1024x1024"

        )

        st.image(base64.b64decode(lighting_img.data[0].b64_json))



        # ======= 4) 3D Render =======

        st.markdown("#### 🏡 3D Render")

        render_img = client.images.generate(

            model="gpt-image-1",

            prompt=f"3D render of a {style} room with budget {budget} SAR. Room: {description}. Purpose: {purpose}. Realistic Pinterest-level.",

            size="1024x1024"

        )

        st.image(base64.b64decode(render_img.data[0].b64_json))



    except Exception as e:

        st.error(f"Image generation failed: {e}")

        return None




# ---------- WHEN BUTTON CLICKED ----------

if clicked:

    if not description.strip():

        st.warning("اكتبي وصف الغرفة أول 🙏")

    else:

        with st.spinner("✨ Agents are analyzing your space..."):

            # 1) استدعاء الوكلاء

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



            # 2) ملخص عام للعميل

            summary_prompt = f"""

You are a senior interior designer.



Create a friendly client-facing summary (max 2 paragraphs + bullet list)

for this room design in English:



Room: {description}

Style: {style}

Purpose: {purpose}

Budget: {budget} SAR



Summarize the key ideas from:

- Architectural / layout plan

- Furniture plan

- Color palette plan

"""



            summary_answer = client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[

                    {

                        "role": "system",

                        "content": "You summarize interior design plans in simple, client-friendly English.",

                    },

                    {

                        "role": "user",

                        "content": summary_prompt,

                    },

                ],

                temperature=0.7,

            ).choices[0].message.content



            # 3) توليد الصورة (اختياري)

            image_bytes = None

            if generate_moodboard:

                image_bytes = generate_moodboard_image(

                    description, style, purpose, budget, uploaded_photo

                )



            # 4) حفظ النّتائج في session_state

            st.session_state["results"] = {

                "summary": summary_answer,

                "architect": architect_answer,

                "furniture": furniture_answer,

                "colors": color_answer,

                "image_bytes": image_bytes,

            }



# ---------- RIGHT: RESULTS ----------

with right_col:

    st.markdown("### 📊 Design Analysis")



    # ✨ Tabs always appear directly under the title (fixed)

    tab_overview, tab_arch, tab_furniture, tab_colors, tab_moodboard, tab_3d = st.tabs(

        ["Overview", "Architect Plan", "Furniture Plan", "Color Palette", "AI Moodboard", "3D Render"]

    )


# Load results safely

if "results" in st.session_state:

    results = st.session_state["results"]

else:

    results = None


    with tab_overview:

        if results["summary"]:

            st.markdown("### 🧾 Quick Summary")

            st.markdown(results["summary"])

        else:

            st.info("اضغطي على **Generate Full Interior Plan** بعد ما تعبّين بيانات الغرفة.")



    with tab_architect:

        if results["architect"]:

            st.markdown("### 🏛️ Architect / Layout Plan")

            st.markdown(results["architect"])

        else:

            st.info("سيظهر هنا مخطط توزيع الغرفة (layout) بعد تشغيل الأداة.")



    with tab_furniture:

        if results["furniture"]:

            st.markdown("### 🪑 Furniture & Budget Plan")

            st.markdown(results["furniture"])

        else:

            st.info("سيظهر هنا تحليل الأثاث واقتراح القطع بعد تشغيل الأداة.")



    with tab_colors:

        if results["colors"]:

            st.markdown("### 🎨 Color Palette & Materials")

            st.markdown(results["colors"])

        else:

            st.info("سيظهر هنا اقتراح الألوان والمواد بعد تشغيل الأداة.")

with tab_moodboard:



    st.markdown("## 🎨 AI Moodboard (Furniture + Colors + Lighting + 3D Render)")



    col1, col2= st.columns(2)



    # ----- 1) Furniture Pieces -----

    with col1:

        furniture_img = client.images.generate(

            model="gpt-image-1",

            prompt=f"Moodboard showing ONLY furniture pieces for a {style} room.",

            size="1024x1024"

        )

        st.markdown("#### 🪑 Furniture")

        st.image(base64.b64decode(furniture_img.data[0].b64_json))


    # ----- 2) Colors + Materials -----

    with col2:

        colors_img = client.images.generate(

            model="gpt-image-1",

            prompt=f"Color palette + materials for a {style} interior.",

            size="1024x1024"

        )

        st.markdown("#### 🎨 Colors")

        st.image(base64.b64decode(colors_img.data[0].b64_json))


        except Exception as e:

            st.error("3D render failed: " + str(e))

