import streamlit as st
import os
from openai import OpenAI

# --- إعداد مفتاح API ---
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- واجهة التطبيق ---
st.set_page_config(page_title="Interior AI Designer", page_icon="🎨", layout="wide")

st.title("🎨 Interior AI Designer")
st.write("Your personal AI-powered interior design consultant.")

description = st.text_area("Describe your room & purpose:")
style = st.selectbox("Select style:", ["Modern", "Minimal", "Classic", "Boho", "Luxury"])
budget = st.number_input("Your budget (SAR):", min_value=500, max_value=100000)

if st.button("Analyze My Design"):
with st.spinner("Analyzing your room..."):
prompt = f"""
You are a senior architect and interior designer.

Analyze this room:
Description: {description}
Style: {style}
Budget: {budget}

Provide:
1. Full design concept
2. Color palette with HEX codes
3. Lighting plan
4. Furniture recommendations (name + why + price)
5. Mistakes to avoid
6. Layout tips

Return in clean formatted markdown.
"""

response = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": prompt}]
)

answer = response.choices[0].message["content"]
st.markdown(answer)
