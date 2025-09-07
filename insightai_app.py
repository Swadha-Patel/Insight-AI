import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import time

# -------------------------------
# Fix file watcher error for Streamlit Cloud
# -------------------------------
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="InsightAI - Feedback Analyzer", page_icon="🤖", layout="centered")

st.title("🤖 InsightAI - Customer Feedback Analyzer")
st.markdown("Upload customer feedback and let AI uncover pain points, feature requests, and suggested improvements in a clean, readable format.")

# -------------------------------
# Load API Key safely from Streamlit Secrets
# -------------------------------
api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ No OpenAI API key found. Please add it in Streamlit Secrets to run the app.")
else:
    client = OpenAI(api_key=api_key)

# -------------------------------
# AI Analysis Function
# -------------------------------
def get_ai_insights(feedback_text):
    models = ["gpt-4o", "gpt-3.5-turbo"]
    prompt = f"""
    Analyze the following user feedback and output in markdown format with headings and bullets like this:

    ### Top Pain Points
    - point 1
    - point 2

    ### Top Feature Requests
    - request 1
    - request 2

    ### Recommended Improvements
    - improvement 1
    - improvement 2

    Feedback:
    {feedback_text}
    """

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a product manager analyzing user feedback for clear, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700
            )
            return response.choices[0].message.content
        except Exception as e:
            if "insufficient_quota" in str(e) or "model_not_found" in str(e):
                continue
            return f"⚠️ Error analyzing feedback: {e}"
    return "⚠️ All models failed. Please check your OpenAI quota or billing settings."

# -------------------------------
# Helper to render each section with colors & bullets
# -------------------------------
def render_section(title, content, color):
    st.markdown(f"<h4 style='background-color:{color}; padding:6px; border-radius:5px;'>{title}</h4>", unsafe_allow_html=True)
    for line in content.split("\n"):
        if line.strip().startswith("-"):
            st.markdown(line)

# -------------------------------
# File Upload Section
# -------------------------------
st.markdown("### Step 1: Upload Your Feedback Data")
st.caption("Upload a CSV file with a column named 'feedback'. Max size: 200MB")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
st.markdown("<br>", unsafe_allow_html=True)

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.success(f"✅ File uploaded successfully! {len(data)} feedback records found.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📄 Preview Uploaded Data"):
        st.dataframe(data.head())

    # -------------------------------
    # Analysis Section
    # -------------------------------
    st.markdown("### Step 2: Analyze with AI")
    if 'feedback' in data.columns and api_key:
        if st.button("Run Analysis", use_container_width=True):
            with st.spinner("Analyzing feedback with AI..."):
                feedback_text = " ".join(data['feedback'].astype(str).tolist())
                time.sleep(1)
                ai_output = get_ai_insights(feedback_text)

            st.markdown("### Step 3: Results")
            sections = {"Top Pain Points": "", "Top Feature Requests": "", "Recommended Improvements": ""}
            current = None

            for line in ai_output.split("\n"):
                if line.startswith("### "):
                    current = line.replace("### ", "").strip()
                elif current in sections:
                    sections[current] += line + "\n"

            render_section("Top Pain Points", sections["Top Pain Points"], "#ffe0b2")
            render_section("Top Feature Requests", sections["Top Feature Requests"], "#bbdefb")
            render_section("Recommended Improvements", sections["Recommended Improvements"], "#c8e6c9")
    else:
        st.error("❌ The uploaded CSV must have a column named 'feedback'.")
else:
    st.info("📂 Please upload a CSV file to get started.")
