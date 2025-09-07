import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import time
import re

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="InsightAI - Feedback Analyzer", page_icon="🤖", layout="centered")

st.markdown(
    """
    <h1 style='text-align:center; color:#4CAF50;'>InsightAI - Customer Feedback Analyzer</h1>
    <p style='text-align:center; font-size:18px;'>Upload customer feedback and let AI uncover pain points, feature requests, and suggested improvements instantly.</p>
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
# Function to extract sections for tabs
# -------------------------------
def extract_sections(ai_text):
    sections = {"Pain Points": "", "Feature Requests": "", "Suggested Improvements": ""}
    current_section = None
    for line in ai_text.split("\n"):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if "pain point" in line_stripped.lower():
            current_section = "Pain Points"
        elif "feature request" in line_stripped.lower():
            current_section = "Feature Requests"
        elif "improvement" in line_stripped.lower():
            current_section = "Suggested Improvements"
        if current_section and not any(h in line_stripped.lower() for h in ["pain point", "feature request", "improvement"]):
            sections[current_section] += line_stripped + "\n"
    return sections

# -------------------------------
# Function to get AI insights with error handling & fallback
# -------------------------------
def get_ai_insights(feedback_text):
    models = ["gpt-4o", "gpt-3.5-turbo"]
    prompt = f"""
    Analyze the following user feedback and provide three sections clearly labeled:
    1. Top Pain Points
    2. Top Feature Requests
    3. Suggested Improvements (specific actions to fix pain points or deliver requested features)

    Feedback:
    {feedback_text}
    """

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a product manager analyzing user feedback for actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
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

            # Extract sections for tabs
            sections = extract_sections(ai_output)

            # Tabs for cleaner UI
            tab1, tab2, tab3 = st.tabs(["📉 Pain Points", "💡 Feature Requests", "🚀 Suggested Improvements"])
            with tab1:
                st.markdown(f"<div style='background-color:#fff3e0;padding:10px;border-radius:5px;'>{sections['Pain Points']}</div>", unsafe_allow_html=True)
            with tab2:
                st.markdown(f"<div style='background-color:#e3f2fd;padding:10px;border-radius:5px;'>{sections['Feature Requests']}</div>", unsafe_allow_html=True)
            with tab3:
                st.markdown(f"<div style='background-color:#e8f5e9;padding:10px;border-radius:5px;'>{sections['Suggested Improvements']}</div>", unsafe_allow_html=True)

    elif 'feedback' not in data.columns:
        st.error("❌ The uploaded CSV must have a column named 'feedback'.")
else:
    st.info("📂 Please upload a CSV file to get started.")


