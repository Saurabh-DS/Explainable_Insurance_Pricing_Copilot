import streamlit as st
import requests
import os

# Page configuration
st.set_page_config(
    page_title="Insurance Pricing Copilot",
    page_icon="🛡️",
    layout="wide"
)

# API URL (internal Docker network or localhost)
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🛡️ Explainable Insurance Pricing Copilot")
st.markdown("""
This tool uses a **LightGBM Pricing Model** with **SHAP explainability** and 
**Retrieval-Augmented Generation (RAG)** to explain your insurance premiums.
""")

# Sidebar for inputs
st.sidebar.header("📋 Customer Profile")

age = st.sidebar.slider("Age", 18, 80, 25)
postcode_risk = st.sidebar.slider("Postcode Risk (0.0 Safe, 1.0 High)", 0.0, 1.0, 0.5)
vehicle_group = st.sidebar.slider("Vehicle Group (1 Economy, 50 Luxury)", 1, 50, 15)
claims_count = st.sidebar.number_input("Number of Claims", 0, 5, 0)
ncb_years = st.sidebar.number_input("No Claims Bonus (Years)", 0, 10, 3)

if st.sidebar.button("Calculate & Explain Premium"):
    profile = {
        "age": age,
        "postcode_risk": postcode_risk,
        "vehicle_group": vehicle_group,
        "claims_count": claims_count,
        "ncb_years": ncb_years
    }
    
    with st.spinner("🤖 Copilot is analyzing the data..."):
        try:
            response = requests.post(f"{API_URL}/explain", json=profile)
            if response.status_code == 200:
                result = response.json()
                explanation = result["explanation"]
                
                st.success("Analysis Complete!")
                st.subheader("💡 Copilot's Explanation")
                st.markdown(explanation)
                
                # SHAP logging note
                st.info("ℹ️ This prediction and its SHAP values have been logged to `logs/shap_results.jsonl` for audit compliance.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Could not connect to the API: {e}")

# Instructions for beginners
with st.expander("ℹ️ How it works"):
    st.write("""
    1. **ML Prediction**: A LightGBM model predicts the premium based on historical data.
    2. **SHAP Attribution**: We calculate exactly how much each factor (like age) added to or subtracted from your price.
    3. **RAG Search**: We search original Underwriting Guidelines to find human-readable rules that justify the ML decision.
    4. **Agent Synthesis**: A LangGraph agent combines these outputs into a professional explanation.
    """)
