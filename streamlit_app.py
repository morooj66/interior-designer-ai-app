import os

import base64

from io import BytesIO



import streamlit as st

from openai import OpenAI

from PIL import Image



# ------------------ SETUP ------------------

st.set_page_config(page_title="AI Interior Studio", page_icon="🛋️", layout="wide")



api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:

    st.error("⚠️ Please upload your OPENAI_API_KEY in Settings → Secrets.")

    st.stop()



client = OpenAI(api_key=api_key)



# ------------------ SIDEBAR ------------------

with st.sidebar:

    st.title("🛋️ AI Interior Studio")

    st.caption("Multi-Agent Smart Interior Designer")

    st.markdown("""

- 🏛️ Architect Agent  

- 🪑 Furniture Agent  

- 🎨 Color Palette Expert  

- 🖼️ AI Moodboard  

- 🏡 3D Render Generator  

""")

    st.markdown("---")

    st.markdown("Made by **Morooj** ✨")



# ------------------ SESSION ------------------

if "results" not in st.session_state:

    st.session_state["results"] = None



# ------------------ FORM ------------------

left, right = st.columns([1, 2])



with left:

    st.markdown("### 🧾 Room Details")



    description = st.text_area(

        "Room Description",

        placeholder="Example: Luxury living room, beige tones, large window, soft lighting, modern furniture..."

    )



    style = st.selectbox(

        "Preferred Style",

        ["Modern", "Minimal", "Classic", "Boho", "Luxury"],

    )



    purpose = st.text_input(

        "Purpose of the room",

        value="Living, relaxing, hosting guests..."

    )



    budget = st.number_input(

        "Budget (SAR)",

        min_value=500,

        max_value=200000,

        value=5000,

        step=500,

    )



    uploaded_photo = st.file_uploader(

        "Upload a room photo (optional)",

        type=["jpg", "jpeg", "png"]

    )



    generate_moodboard = st.checkbox("Generate Moodboard + 3D Render", value=True)



    clicked = st.button("✨ Generate Full Interior Plan", use_container_width=True)



# ------------------ AGENT FUNCTION ------------------

def call_agent(role, description, style, purpose, budget):

    prompt = f"""

You are {role}.



Room description: {description}

Style: {style}

Purpose: {purpose}

Budget: {budget} SAR



Give a structured plan in Markdown using clean bullet points.

"""



    try:

        res = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {"role": "system", "content": "You are a senior interior designer."},

                {"role": "user", "content": prompt},

            ],

            temperature=0.8,

        )

        return res.choices[0].message.content



    except Exception as e:

        return f"⚠️ Error: {e}"



# ------------------ IMAGE GENERATION ------------------

def generate_image(prompt):

    try:

        result = client.images.generate(

            model="gpt-image-1",

            prompt=prompt,

            size="1024x1024"

        )

        b64 = result.data[0].b64_json

        return base64.b64decode(b64)

    except Exception as e:

        st.error("Image generation failed: " + str(e))

        return None



# ------------------ HANDLE SUBMIT ------------------

if clicked:

    if not description.strip():

        st.warning("اكتبي وصف الغرفة أول 🙏")

    else:

        with st.spinner("✨ Agents are working on your interior plan..."):



            summary = call_agent(

                "a senior interior consultant summarizing the full project",

                description, style, purpose, budget

            )



            architect = call_agent(

                "an architect and layout planning expert",

                description, style, purpose, budget

            )



            furniture = call_agent(

                "a furniture sourcing and styling expert",

                description, style, purpose, budget

            )



            colors = call_agent(

                "a color palette and materials specialist",

                description, style, purpose, budget

            )



            moodboard_img = None

            render_img = None



            if generate_moodboard:

                moodboard_img = generate_image(

                    f"Moodboard for {style} interior: furniture, colors, materials, lighting. {description}"

                )



                render_img = generate_image(

                    f"Full 3D render, luxury Pinterest style, {style} interior. {description}. Cinematic lighting, realistic textures."

                )



            st.session_state["results"] = {

                "summary": summary,

                "architect": architect,

                "furniture": furniture,

                "colors": colors,

                "moodboard": moodboard_img,

                "render": render_img,

            }



# ------------------ RESULTS ------------------

with right:

    st.markdown("### 📊 Design Analysis")



    tabs = st.tabs([

        "Overview", 

        "Architect Plan", 

        "Furniture Plan", 

        "Color Palette", 

        "AI Moodboard", 

        "3D Render"

    ])



    results = st.session_state["results"]



    if results:



        with tabs[0]:

            st.markdown("## 🧾 Overview")

            st.markdown(results["summary"])



        with tabs[1]:

            st.markdown("## 🏛️ Architect Plan")

            st.markdown(results["architect"])



        with tabs[2]:

            st.markdown("## 🪑 Furniture Plan")

            st.markdown(results["furniture"])



        with tabs[3]:

            st.markdown("## 🎨 Color Palette")

            st.markdown(results["colors"])



        with tabs[4]:

            st.markdown("## 🎨 Moodboard")

            if results["moodboard"]:

                st.image(results["moodboard"])

            else:

                st.info("No moodboard generated.")



        with tabs[5]:

            st.markdown("## 🏡 3D Render")

            if results["render"]:

                st.image(results["render"])

            else:

                st.info("No 3D render generated.")

    else:

        st.info("املئي البيانات واضغطي على الزر لعرض النتائج.")


