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

st.markdown(
    """
    <h1 style='text-align:center; color:#4CAF50;'>InsightAI - Customer Feedback Analyzer</h1>
    <p style='text-align:center; font-size:18px;'>Upload customer feedback and let AI uncover pain points, feature requests, and suggested improvements in a clean, readable format.</p>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Load API Key safely from Streamlit Secrets
# -------------------------------
api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ No OpenAI API key found. Please add it in Streamlit Secrets to run the app.")
else:
    client = OpenAI(api_key=api_key)

# -------------------------------
# Function to get AI insights with proper markdown
# -------------------------------
def get_ai_insights(feedback_text):
    models = ["gpt-4o", "gpt-3.5-turbo"]
    prompt = f"""
    Analyze the following user feedback and output in markdown format with headings and bullets exactly like this:

    ### Top Pain Points
    - First pain point
    - Second pain point

    ### Top Feature Requests
    - First request
    - Second request

    ### Recommended Improvements
    - First improvement
    - Second improvement

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
            error_msg = str(e)
            if "insufficient_quota" in error_msg or "model_not_found" in error_msg:
                if model != models[-1]:
                    continue
                else:
                    return "⚠️ All models failed. Please check your OpenAI quota or billing settings."
            else:
                return f"⚠️ Error analyzing feedback: {e}"

# -------------------------------
# Helper to render each section separately with colors
# -------------------------------
def render_section(title, content, color):
    st.markdown(f"<h4 style='color:black; background-color:{color}; padding:6px; border-radius:5px;'>{title}</h4>", unsafe_allow_html=True)
    for line in content.split("\n"):
        if line.strip().startswith("-"):
            st.markdown(line)

# -------------------------------
# File Upload Section
# -------------------------------
st.markdown("<h3 style='color:#2196F3;'>Step 1: Upload Your Feedback Data</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV with a 'feedback' column", type="csv", help="Make sure your CSV has a column named 'feedback'.")

# -------------------------------
# Analysis Section
# -------------------------------
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.success(f"✅ File uploaded successfully! {len(data)} feedback records found.")

    with st.expander("Preview Uploaded Data"):
        st.dataframe(data.head())

    if 'feedback' in data.columns and api_key:
        st.markdown("<h3 style='color:#2196F3;'>Step 2: Analyze with AI</h3>", unsafe_allow_html=True)
        if st.button("Run Analysis", use_container_width=True):
            with st.spinner("Analyzing feedback with AI..."):
                feedback_text = " ".join(data['feedback'].astype(str).tolist())
                time.sleep(1)
                ai_output = get_ai_insights(feedback_text)

            st.markdown("<h3 style='color:#4CAF50;'>Step 3: Results</h3>", unsafe_allow_html=True)

            # Split sections properly
            sections = {"Top Pain Points": "", "Top Feature Requests": "", "Recommended Improvements": ""}
            current = None
            for line in ai_output.split("\n"):
                if line.startswith("### "):
                    current = line.replace("### ", "").strip()
                elif current in sections:
                    sections[current] += line + "\n"

            # Render each section with colors & bullets
            render_section("Top Pain Points", sections["Top Pain Points"], "#ffe0b2")
            render_section("Top Feature Requests", sections["Top Feature Requests"], "#bbdefb")
            render_section("Recommended Improvements", sections["Recommended Improvements"], "#c8e6c9")

    elif 'feedback' not in data.columns:
        st.error("❌ The uploaded CSV must have a column named 'feedback'.")
else:
    st.info("📂 Please upload a CSV file to get started.")
