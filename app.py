import streamlit as st
import pandas as pd
import numpy as np
from train_model import predict_target_split

def extract_workout_details(workout):
    """Parse workout string into reps, distance, and rest time."""
    import re
    match = re.match(r"(\d+)\*(\d+)(m|min) \((\d+)\)", workout)
    if match:
        reps = int(match.group(1))
        distance = int(match.group(2))
        rest_time = int(match.group(4))
        return reps, distance, rest_time
    return None, None, None

# Hardcoded default erg splits (no CSV loading)
default_2k = 95.0    # 1:36 per 500m
default_5k = 100.0   # 1:48 per 500m
default_30at20 = 107.0  # 2:00 per 500m

# Streamlit UI
st.image("Rowing Workout Predictor logo.png", use_container_width=True)
st.title("Rowing Workout Predictor")
st.write("Enter your erg test splits and workout details to get a personalized target split.")
st.write("Workout format: reps * distance (rest minutes), e.g., 8*500m (2)")
st.write("Valid ranges: Reps (3–50), Distance (300–5000m), Rest (1–9min)")

# User input for erg splits
st.subheader("Input Erg Test PBs")

# 2k Split
st.write("**2000m Split**")
col1, col2 = st.columns(2)
with col1:
    minutes_2k = st.number_input("Minutes (2k)", min_value=1, max_value=2, value=int(default_2k // 60), key="2k_min")
with col2:
    seconds_2k = st.number_input("Seconds (2k)", min_value=0.0, max_value=59.9, value=default_2k % 60, step=0.1, key="2k_sec")
user_2k = minutes_2k * 60 + seconds_2k

# 5k Split
st.write("**5000m Split**")
col3, col4 = st.columns(2)
with col3:
    minutes_5k = st.number_input("Minutes (5k)", min_value=1, max_value=3, value=int(default_5k // 60), key="5k_min")
with col4:
    seconds_5k = st.number_input("Seconds (5k)", min_value=0.0, max_value=59.9, value=default_5k % 60, step=0.1, key="5k_sec")
user_5k = minutes_5k * 60 + seconds_5k

# 30@20 Split
st.write("**30@20 Split**")
col5, col6 = st.columns(2)
with col5:
    minutes_30at20 = st.number_input("Minutes (30@20)", min_value=1, max_value=3, value=int(default_30at20 // 60), key="30at20_min")
with col6:
    seconds_30at20 = st.number_input("Seconds (30@20)", min_value=0.0, max_value=59.9, value=default_30at20 % 60, step=0.1, key="30at20_sec")
user_30at20 = minutes_30at20 * 60 + seconds_30at20

# Use user-input erg splits
erg_splits = (user_2k, user_5k, user_30at20)

# Display erg splits
st.header("Erg Workout Calculator")
st.write(f"**2000m Split:** {int(user_2k // 60)}:{user_2k % 60:.1f} per 500m")
st.write(f"**5000m Split:** {int(user_5k // 60)}:{user_5k % 60:.1f} per 500m")
st.write(f"**30@20 Split:** {int(user_30at20 // 60)}:{user_30at20 % 60:.1f} per 500m")

# Workout input
if "workout_input" not in st.session_state:
    st.session_state.workout_input = ""
st.text_input("Enter Workout:", value=st.session_state.workout_input, key="workout_input")

# Process workout
if st.session_state.workout_input:
    reps, interval_distance, rest_time = extract_workout_details(st.session_state.workout_input)
    if reps is not None:
        if not (1 <= reps <= 50):
            st.error("Reps must be between 3 and 50.")
        elif not (50 <= interval_distance <= 5000):
            st.error("Distance must be between 300m and 5000m.")
        elif not (1 <= rest_time <= 9):
            st.error("Rest time must be between 1 and 9 minutes.")
        else:
            predicted_split = predict_target_split(interval_distance, reps, rest_time, erg_splits) + 2.5  # Add 2.5 seconds
            minutes = int(predicted_split // 60)
            seconds = round(predicted_split % 60, 1)
            st.success(f"Recommended Target Split: {minutes}:{seconds:04.1f} per 500m")
    else:
        st.error("Invalid format. Use: reps*distance (rest minutes), e.g., 8*500m (2)")

st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write("Rowing Workout Predictor © ¦ Created by Tom Loosley ¦ Published in 2025")
st.markdown("Found a problem? <a href='mailto:loosleytom@gmail.com'>Report an issue</a>", unsafe_allow_html=True)
