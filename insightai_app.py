import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import time

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="InsightAI - Feedback Analyzer", page_icon="🤖", layout="centered")
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>InsightAI - Customer Feedback Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload customer feedback and let AI uncover top pain points and feature requests instantly.</p>", unsafe_allow_html=True)

# -------------------------------
# Load API Key safely from Streamlit Secrets
# -------------------------------
api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ No OpenAI API key found. Please add it in Streamlit Secrets to run the app.")
else:
    client = OpenAI(api_key=api_key)

# -------------------------------
# Function to get AI insights with error handling & fallback
# -------------------------------
def get_ai_insights(feedback_text):
    models = ["gpt-4o", "gpt-3.5-turbo"]
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a product analyst. Summarize top pain points and feature requests from user feedback."},
                    {"role": "user", "content": feedback_text}
                ],
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg or "model_not_found" in error_msg:
                if model != models[-1]:
                    continue  # Try next model if quota or access error
                else:
                    return "⚠️ All models failed. Please check your OpenAI quota or billing settings."
            else:
                return f"⚠️ Error analyzing feedback: {e}"

# -------------------------------
# File Upload Section
# -------------------------------
st.subheader("Step 1: Upload Your Feedback Data")
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
        st.subheader("Step 2: Analyze with AI")
        if st.button("Run Analysis"):
            with st.spinner("Analyzing feedback with AI..."):
                feedback_text = " ".join(data['feedback'].astype(str).tolist())
                time.sleep(1)  # Simulate processing delay
                insights = get_ai_insights(feedback_text)

            # Display results nicely
            st.subheader("Step 3: Insights from AI")
            st.markdown(f"<div style='background-color:#f9f9f9;padding:10px;border-radius:5px;'>{insights}</div>", unsafe_allow_html=True)

    elif 'feedback' not in data.columns:
        st.error("❌ The uploaded CSV must have a column named 'feedback'.")
else:
    st.info("📂 Please upload a CSV file to get started.")

