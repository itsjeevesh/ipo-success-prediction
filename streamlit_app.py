import streamlit as st
import requests
import pandas as pd
import pdfplumber
import streamlit.components.v1 as components

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="IPO Success Predictor",
    layout="wide"
)

# ===============================
# Risk + Investment Logic
# ===============================

def get_investment_insight(probability):
    if probability >= 0.75:
        return "Low Risk", "Strong Buy", "success"
    elif probability >= 0.5:
        return "Moderate Risk", "Invest", "warning"
    elif probability >= 0.3:
        return "High Risk", "Invest with Caution", "warning"
    else:
        return "Very High Risk", "Avoid", "error"


# ===============================
# Summary Generator
# ===============================

def generate_summary(prediction, explanation):

    positive_words = [w for w, s in explanation if s > 0][:5]
    negative_words = [w for w, s in explanation if s < 0][:5]

    pos_text = ", ".join(positive_words)
    neg_text = ", ".join(negative_words)

    if prediction.lower().startswith("successful"):

        summary = f"""
The model predicts this IPO is likely to be **successful**.

Positive signals include: {pos_text}.

However, potential risks include: {neg_text}.
"""

    else:

        summary = f"""
The model predicts this IPO may be **unsuccessful**.

Negative indicators include: {neg_text}.

Some positives ({pos_text}) exist but are not strong enough.
"""

    return summary


# ===============================
# Sidebar
# ===============================

st.sidebar.title("📊 Model Information")

st.sidebar.markdown(""" 
**Input:** DRHP Prospectus Text  
**Dataset:** Indian IPO Dataset  

**Performance**
- Accuracy: **91%**
- ROC-AUC: **0.99**

**Explainability**
- LIME (Local explanations)
""")

st.sidebar.markdown("---")
st.sidebar.info("Upload DRHP text or PDF to predict IPO success probability.")


# ===============================
# Title
# ===============================

st.title("📈 IPO Success Prediction Platform")

st.markdown("""
Analyze **DRHP documents** and predict IPO success with AI-powered insights.
""")


# ===============================
# Tabs
# ===============================

tab1, tab2 = st.tabs(["Single Prediction", "Batch Prediction"])


# ==========================================================
# TAB 1 — Single Prediction
# ==========================================================

with tab1:

    st.header("Predict IPO Success")

    col1, col2 = st.columns(2)

    with col1:
        text_input = st.text_area("Paste DRHP Text", height=300)

    with col2:
        uploaded_file = st.file_uploader("Upload DRHP PDF", type=["pdf"])

        extracted_text = ""

        if uploaded_file:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() or ""
            st.success("PDF text extracted successfully")

    final_text = extracted_text if extracted_text else text_input

    if st.button("Predict IPO Success"):

        if final_text.strip() == "":
            st.warning("Please enter DRHP text or upload a PDF.")
        else:

            payload = {"text": final_text}

            try:
                response = requests.post(f"{API_URL}/predict", json=payload)
                result = response.json()

                probability = result["probability"]
                prediction = result["prediction"]

                risk, recommendation, level = get_investment_insight(probability)

                st.subheader("Prediction Result")

                colA, colB = st.columns(2)

                with colA:
                    st.metric("IPO Success Probability", f"{probability:.2f}")

                    # Better progress bar
                    st.progress(int(probability * 100))

                with colB:
                    if prediction.lower() == "successful ipo":
                        st.success("Predicted Outcome: Successful IPO")
                    else:
                        st.error("Predicted Outcome: Unsuccessful IPO")

                # ===============================
                # 🔥 NEW: INVESTMENT INSIGHT
                # ===============================

                st.subheader("Investment Insight")

                if level == "success":
                    st.success(f"🟢 {recommendation} — {risk}")
                elif level == "warning":
                    st.warning(f"🟡 {recommendation} — {risk}")
                else:
                    st.error(f"🔴 {recommendation} — {risk}")

                st.markdown(f"""
**Interpretation:**  
This IPO falls under **{risk}** category.  
Recommendation: **{recommendation}**.
""")

                # ===============================
                # LIME Explanation
                # ===============================

                st.subheader("Explanation (Important Words)")

                exp = requests.post(f"{API_URL}/explain", json=payload)
                explanation = exp.json()

                if "html" in explanation:
                    components.html(explanation["html"], height=600)

                elif "explanation" in explanation:
                    for word, score in explanation["explanation"]:
                        if score > 0:
                            st.write(f"🟢 **{word}** → {score:.3f}")
                        else:
                            st.write(f"🔴 **{word}** → {score:.3f}")

                # ===============================
                # Plain English Summary
                # ===============================

                if "explanation" in explanation:

                    summary = generate_summary(
                        prediction,
                        explanation["explanation"]
                    )

                    st.subheader("AI Explanation (Plain English)")
                    st.write(summary)

            except Exception as e:
                st.error(f"API error: {e}")


# ==========================================================
# TAB 2 — Batch Prediction
# ==========================================================

with tab2:

    st.header("Batch IPO Prediction")

    csv_file = st.file_uploader("Upload CSV", type=["csv"], key="batch_csv")

    if csv_file:

        df = pd.read_csv(csv_file)
        st.dataframe(df.head())

        if st.button("Run Batch Prediction"):

            predictions = []
            probabilities = []
            risks = []
            recommendations = []

            for text in df["text"]:

                payload = {"text": text}
                response = requests.post(f"{API_URL}/predict", json=payload)
                result = response.json()

                prob = result["probability"]
                risk, rec, _ = get_investment_insight(prob)

                predictions.append(result["prediction"])
                probabilities.append(prob)
                risks.append(risk)
                recommendations.append(rec)

            df["prediction"] = predictions
            df["probability"] = probabilities
            df["risk"] = risks
            df["recommendation"] = recommendations

            st.success("Batch prediction completed")
            st.dataframe(df)

            st.download_button(
                "Download Results",
                df.to_csv(index=False),
                "ipo_predictions.csv",
                "text/csv"
            )


# ===============================
# Footer
# ===============================

st.markdown("---")

st.markdown("""
**IPO Success Prediction System**

AI-powered analysis using Machine Learning and Explainable AI.
""")