import streamlit as st
from openai import OpenAI
import os

# Load API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Page settings
st.set_page_config(page_title="AI Interior Studio", page_icon="🛋️", layout="wide")

st.title("🛋️ AI Interior Studio")
st.write("Your multi-agent interior design consultant: Architect, Furniture Expert, and Color Stylist.")

# --------------------------
# USER INPUTS
# --------------------------
col1, col2 = st.columns(2)

with col1:
 description = st.text_area(
    "Room Description",
    placeholder="Example: Small bedroom 3x4m, wants cozy modern vibes..."
)
 style = st.selectbox(
      "Preferred Style",
      ["Modern", "Minimal", "Classic", "Boho", "Luxury"]
    )

with col2:
    budget = st.number_input("Budget (SAR)", min_value=500, max_value=100000)
    purpose = st.text_input("Purpose of the Room", "Sleeping, studying, relaxing...")

# --------------------------
# BUTTON ACTION
# --------------------------
if st.button("Generate Full Interior Plan"):
    with st.spinner("Agents are analyzing your space…"):

# --------------------------
# AGENT 1 → ARCHITECT
# --------------------------
       architect_prompt = f"""
       You are a senior architect.

 Task:
 Analyze the room and generate:
- Full design concept
- Room flow
- Space functionality improvements
- Best layout logic

Inputs:
Description: {description}
Style: {style}
Purpose: {purpose}
Budget: {budget}

Return in clean markdown.
"""

architect = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": architect_prompt}]
).choices[0].message["content"]

# --------------------------
# AGENT 2 → FURNITURE EXPERT
# --------------------------
furniture_prompt = f"""
You are an expert in furniture selection.

Task:
Provide:
- Shopping list
- Product names
- Prices (Saudi market range)
- Why each item fits the room
- Furniture arrangement tips

Inputs:
Room: {description}
Style: {style}
Purpose: {purpose}
Budget: {budget}

Return in a table + clean markdown.
"""

furniture = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": furniture_prompt}]
).choices[0].message["content"]

# --------------------------
# AGENT 3 → COLOR PALETTE + DECOR
# --------------------------
color_prompt = f"""
You are a senior interior stylist.

Task:
Provide:
- Color palette with HEX codes
- Wall paint suggestions
- Decor accessories
- Lighting plan
- Moodboard keywords

Inputs:
Room: {description}
Style: {style}

Return in clean markdown.
"""

colors = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": color_prompt}]
).choices[0].message["content"]

# --------------------------
# OUTPUT SECTIONS
# --------------------------
st.success("Design generated successfully!")

st.subheader("🏛️ Architect Analysis")
st.markdown(architect)

st.subheader("🪑 Furniture Expert Recommendations")
st.markdown(furniture)

st.subheader("🎨 Color Palette & Styling")
st.markdown(colors)
