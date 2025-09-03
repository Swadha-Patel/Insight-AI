import streamlit as st
import pandas as pd
import openai

st.title("InsightAI - Customer Feedback Analyzer (AI-Powered)")

# Step 1: Enter OpenAI API key
api_key = st.text_input("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", type="password")
if api_key:
    openai.api_key = api_key

st.write("Upload customer feedback data (CSV with a 'feedback' column) to analyze top pain points and feature requests.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded data:")
    st.write(data.head())

    if 'feedback' in data.columns:
        st.write("Analyzing feedback with AI...")

        feedback_text = " ".join(data['feedback'].astype(str).tolist())

        if api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a product analyst. Summarize top pain points and feature requests from user feedback."},
                        {"role": "user", "content": feedback_text}
                    ],
                    max_tokens=200
                )
                insights = response.choices[0].message["content"]
            except Exception as e:
                insights = f"Error analyzing feedback: {e}"
        else:
            insights = "Please enter your OpenAI API key above to analyze feedback."

        st.subheader("Insights from Feedback")
        st.text(insights)
    else:
        st.error("CSV must have a 'feedback' column.")
else:
    st.info("Please upload a CSV file to proceed.")

