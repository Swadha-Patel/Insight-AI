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
# Load API Key from Secrets
# -------------------------------
api_key = os.environ.get("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

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

    if 'feedback' in data.columns:
        st.subheader("Step 2: Analyze with AI")
        if st.button("Run Analysis"):
            with st.spinner("Analyzing feedback with GPT-4..."):
                feedback_text = " ".join(data['feedback'].astype(str).tolist())
                time.sleep(1)  # Simulate processing time
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a product analyst. Summarize top pain points and feature requests from user feedback."},
                            {"role": "user", "content": feedback_text}
                        ],
                        max_tokens=250
                    )
                    insights = response.choices[0].message.content
                except Exception as e:
                    insights = f"Error analyzing feedback: {e}"

            # Display results nicely
            st.subheader("Step 3: Insights from AI")
            st.markdown(f"<div style='background-color:#f9f9f9;padding:10px;border-radius:5px;'>{insights}</div>", unsafe_allow_html=True)

    else:
        st.error("❌ The uploaded CSV must have a column named 'feedback'.")
else:
    st.info("📂 Please upload a CSV file to get started.")

