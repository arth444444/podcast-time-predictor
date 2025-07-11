import streamlit as st
import pandas as pd
import joblib
import os
import requests
import matplotlib.pyplot as plt
import xgboost as xgb


MODEL_PATH = "model.pkl"
FILE_ID = "1YnaNPOt5oj9S1rxdJmZXgL1OWY93Qm0N"
DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

def download_model():
    try:
        st.info("Downloading model...")
        response = requests.get(DOWNLOAD_URL)
        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)
        st.success("Model downloaded successfully.")
    except Exception as e:
        st.error(f"Failed to download model: {e}")

if not os.path.exists(MODEL_PATH):
    download_model()


model = joblib.load(MODEL_PATH)


st.set_page_config(page_title="Podcast Listener Time Predictor", layout="centered")
st.title("🎧 Podcast Listening Time Predictor")
st.markdown("Fill in the podcast episode details below to predict how long people will likely listen to it.")

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        Episode_Length_minutes = st.number_input("Episode Length (minutes)", min_value=1, value=30)
        Genre = st.selectbox("Genre", ["Education", "Comedy", "News", "Business", "Health", "Tech", "Other"])
        Host_Popularity_percentage = st.slider("Host Popularity (%)", 0, 100, 50)
        Publication_Day = st.selectbox("Publication Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        Publication_Time = st.number_input("Publication Time (hour of day)", 0, 23, 10)
        Guest_Popularity_percentage = st.slider("Guest Popularity (%)", 0, 100, 40)
        Number_of_Ads = st.slider("Number of Ads", 0, 10, 2)
        Episode_Sentiment = st.slider("Episode Sentiment Score", -1.0, 1.0, 0.2)

    with col2:
        Episode_Title_num = st.number_input("Title Text Complexity Score", min_value=0.0, value=0.5)
        Ad_Density = Number_of_Ads / max(Episode_Length_minutes, 1)
        Popularity_Diff = Host_Popularity_percentage - Guest_Popularity_percentage
        Popularity_Interaction = Host_Popularity_percentage * Guest_Popularity_percentage
        Host_Popularity_squared = Host_Popularity_percentage ** 2
        Popularity_Average = (Host_Popularity_percentage + Guest_Popularity_percentage) / 2

        st.write(f"**Ad Density:** {Ad_Density:.3f}")
        st.write(f"**Popularity Difference:** {Popularity_Diff}")
        st.write(f"**Popularity Interaction:** {Popularity_Interaction}")
        st.write(f"**Host Popularity Squared:** {Host_Popularity_squared}")
        st.write(f"**Popularity Average:** {Popularity_Average}")

    submitted = st.form_submit_button("Predict Listening Time")

genre_mapping = {
    "Education": 0,
    "Comedy": 1,
    "News": 2,
    "Business": 3,
    "Health": 4,
    "Tech": 5,
    "Other": 6
}
day_mapping = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}

if submitted:
    input_data = pd.DataFrame([{
        "Episode_Length_minutes": Episode_Length_minutes,
        "Genre": genre_mapping.get(Genre, 6),
        "Host_Popularity_percentage": Host_Popularity_percentage,
        "Publication_Day": day_mapping.get(Publication_Day, 0),
        "Publication_Time": Publication_Time,
        "Guest_Popularity_percentage": Guest_Popularity_percentage,
        "Number_of_Ads": Number_of_Ads,
        "Episode_Sentiment": Episode_Sentiment,
        "Episode_Title_num": Episode_Title_num,
        "Ad_Density": Ad_Density,
        "Popularity_Diff": Popularity_Diff,
        "Popularity_Interaction": Popularity_Interaction,
        "Host_Popularity_squared": Host_Popularity_squared,
        "Popularity_Average": Popularity_Average
    }])

    prediction = model.predict(input_data)[0]
    st.success(f"🎯 **Predicted Listening Time:** {prediction:.2f} minutes")

   
    st.subheader("📊 Feature Importance (What matters most?)")
    fig, ax = plt.subplots(figsize=(10, 6))
    xgb.plot_importance(model, ax=ax, importance_type='gain', title='Feature Importance (by Gain)')
    st.pyplot(fig)