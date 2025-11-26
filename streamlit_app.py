import streamlit as st

import os

import base64

from openai import OpenAI



# ------------ API KEY ------------

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:

    st.error("❌ OPENAI_API_KEY is not set. Add it in Streamlit → Settings → Secrets.")

    st.stop()



client = OpenAI(api_key=api_key)



# ------------ PAGE CONFIG ------------

st.set_page_config(

    page_title="AI Interior Studio",

    page_icon="🛋️",

    layout="wide"

)



# ------------ SIDEBAR ------------

with st.sidebar:

    st.markdown("### 🛋️ AI Interior Studio")

    st.write("Multi-agent interior assistant:")

    st.write("- 🧱 Architect agent")

    st.write("- 🛏️ Furniture stylist")

    st.write("- 🎨 Color palette expert")

    st.markdown("---")

    st.markdown("**Made by Morooj **")



# ------------ HEADER ------------

st.markdown(

    "<h1 style='font-size:40px; margin-bottom:0;'>AI Interior Studio</h1>",

    unsafe_allow_html=True,

)

st.markdown(

    "<p style='font-size:16px; color:#cccccc;'>Your multi-agent interior design consultant: Architect, Furniture Expert, and Color Stylist.</p>",

    unsafe_allow_html=True,

)



st.markdown("---")



# ------------ LAYOUT ------------

left_col, right_col = st.columns([1.1, 1.2])



# ------------ LEFT: INPUTS ------------

with left_col:

    st.subheader("📋 Room Details")



    description = st.text_area(

        "Room Description",

        placeholder="Example: Small bedroom 3x4m, one window, wants cozy modern vibes and study corner...",

        height=140

    )



    style = st.selectbox(

        "Preferred Style",

        ["Modern", "Minimal", "Classic", "Boho", "Luxury", "Japandi", "Scandinavian"]

    )



    purpose = st.text_input(

        "Purpose of the Room",

        "Sleeping, studying, relaxing..."

    )



    budget = st.number_input(

        "Budget (SAR)",

        min_value=500,

        max_value=100000,

        value=5000,

        step=500

    )



    st.markdown("### 🖼️ Optional: Room Photo")



    uploaded_image = st.file_uploader(

        "Upload a reference photo (optional)",

        type=["jpg", "jpeg", "png"]

    )



    if uploaded_image is not None:

        st.image(uploaded_image, caption="Uploaded Room Photo", use_column_width=True)



    st.markdown("### 🎨 Optional: Generate AI Moodboard")

    generate_image = st.checkbox("Generate AI moodboard image for this design")



    clicked = st.button("✨ Generate Full Interior Plan", use_container_width=True)



# ------------ HELPER: CALL CHAT ------------

def call_agent(prompt: str) -> str:

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[{"role": "user", "content": prompt}],

    )

    return response.choices[0].message.content





# ------------ RIGHT: RESULTS ------------

with right_col:

    st.subheader("📊 Design Analysis")



    if not clicked:

        st.info("Fill the details on the left, then click **Generate Full Interior Plan**.")

    else:

        if not description.strip():

            st.error("Please write a room description first.")

        else:

            with st.spinner("Agents are working on your interior plan..."):



                # ---------- BUILD BASE CONTEXT ----------

                image_note = ""

                if uploaded_image is not None:

                    image_note = (

                        "\nThe user also uploaded a reference photo. "

                        "Imagine the current furniture and layout from that photo when giving suggestions."

                    )



                base_context = f"""

Room Description: {description}

Style: {style}

Budget: {budget} SAR

Purpose: {purpose}

{image_note}

                """



                # ---------- ARCHITECT AGENT ----------

                architect_prompt = f"""

You are a senior architect and interior space planner.



Analyze this room and create a clear interior architecture plan.



{base_context}



Please provide:



1. **Space & layout concept** – how to arrange zones (sleeping, studying, seating, storage, etc.)

2. **Suggested layout** – describe where the bed, desk, wardrobe, etc. should go.

3. **Wall & ceiling ideas** – niches, panels, shelves, lighting coves (within a realistic budget).

4. **Practical notes** – circulation, natural light, privacy, and ergonomic tips.



Keep it concise but very practical for a real designer.

Output in formatted bullet points.

                """



                # ---------- FURNITURE AGENT ----------

                furniture_prompt = f"""

You are a senior furniture stylist and shopper.



Based on the following room and budget, suggest **realistic furniture plan**.



{base_context}



Return:



1. **Furniture list** (3–8 items) with:

   - Name / type

   - Why it fits the style & function

   - Approximate price range in SAR

2. **Zoning tips** – how to place each item in the room.

3. **Budget summary** – how to distribute the budget (percentages per category).



Keep it realistic for Saudi market prices (rough ranges are okay).

                """



                # ---------- COLOR AGENT ----------

                color_prompt = f"""

You are a color palette and material specialist.



Create a cohesive palette for this room.



{base_context}



Return:



1. **Main base color** (walls) – HEX code + short explanation.

2. **Secondary colors** (furniture / large pieces) – HEX codes + usage.

3. **Accent colors** (decor, cushions, art) – HEX codes + where to use them.

4. **Materials suggestions** – e.g., wood type, metals, fabrics.

5. **Mood description** – 2–3 lines describing the vibe of the space.



Use clear headings and bullet points.

                """



                # ---------- CALL AGENTS ----------

                architect_answer = call_agent(architect_prompt)

                furniture_answer = call_agent(furniture_prompt)

                color_answer = call_agent(color_prompt)



                # ---------- TABS ----------

                tab_overview, tab_architect, tab_furniture, tab_colors, tab_image = st.tabs(

                    ["Overview", "Architect Plan", "Furniture Plan", "Color Palette", "AI Moodboard"]

                )



                with tab_overview:

                    st.markdown("### 🧾 Quick Summary")

                    summary_prompt = f"""

You are a senior interior consultant.



Combine and summarize the following 3 analyses into a short,

client-friendly overview in Arabic and English.



ROOM CONTEXT:

{base_context}



ARCHITECT:

{architect_answer}



FURNITURE:

{furniture_answer}



COLORS:

{color_answer}

                    """

                    summary = call_agent(summary_prompt)

                    st.markdown(summary)



                with tab_architect:

                    st.markdown("### 🏛️ Architect / Layout Plan")

                    st.markdown(architect_answer)



                with tab_furniture:

                    st.marknown("### 🛋️ Furniture & Budget Plan")

                    st.markdown(furniture_answer)



                with tab_colors:

                    st.markdown("### 🎨 Color Palette & Materials")

                    st.markdown(color_answer)



                # ---------- IMAGE GENERATION ----------

                with tab_image:

                    if not generate_image:

                        st.info("Tick **Generate AI moodboard image** on the left to create a visual.")

                    else:

                        try:

                            img_prompt = f"""

Highly realistic interior render, Pinterest level, of a {style} room.

Use this brief:



{base_context}



Focus on:

- composition following the architect & furniture plan,

- color palette similar to the suggested HEX colors,

- soft natural lighting, very aesthetic.



Cinematic, 4K, interior photography style.

                            """



                            img_response = client.images.generate(

                                model="gpt-image-1",

                                prompt=img_prompt,

                                size="1024x1024",

                                n=1

                            )



                            b64_data = img_response.data[0].b64_json

                            img_bytes = base64.b64decode(b64_data)

                            st.image(img_bytes, caption="AI Moodboard Render", use_column_width=True)



                        except Exception as e:

                            st.error(f"Image generation error: {e}")

                            st.info("The text agents still work fine even if image fails.")

