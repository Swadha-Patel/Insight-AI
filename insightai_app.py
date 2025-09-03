
import streamlit as st
import pandas as pd
import openai

st.title("InsightAI - Customer Feedback Analyzer")

st.write("Upload customer feedback data (CSV with a 'feedback' column) to analyze top pain points and feature requests.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded data:")
    st.write(data.head())

    if 'feedback' in data.columns:
        st.write("Analyzing feedback...")
        feedback_text = " ".join(data['feedback'].astype(str).tolist())

        # Mocked OpenAI call since we can't actually call the API here
        # In a real scenario, this would be something like:
        # response = openai.ChatCompletion.create(
        #    model="gpt-4",
        #    messages=[{"role": "system", "content": "Analyze the feedback for pain points and feature requests."},
        #              {"role": "user", "content": feedback_text}]
        # )

        insights = "Top Pain Points: Slow loading times, Poor customer support
Top Feature Requests: Dark mode, Mobile app improvements"
        st.subheader("Insights from Feedback")
        st.text(insights)
    else:
        st.error("CSV must have a 'feedback' column.")
else:
    st.info("Please upload a CSV file to proceed.")
