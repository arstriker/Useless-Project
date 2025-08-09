# Import necessary libraries
import streamlit as st
import cv2
import numpy as np
import tensorflow as tf # Included for structure as requested, though not used in the placeholder


# --- Placeholder ML Model ---
def predict_chai_strength(rgb_color):
    """
    Simulates a machine learning model to predict chai strength based on its RGB color.
    This is a placeholder function using simple if/elif/else logic.

    Args:
        rgb_color (tuple): A tuple containing the average R, G, B values of the chai.

    Returns:
        str: The classification of the chai strength.
    """
    # Calculate the sum of RGB values as a simple measure of brightness.
    # The input from cv2.mean is BGR, so we need to handle it accordingly.
    # The values are usually float, so we convert to int.
    b, g, r, _ = map(int, rgb_color)
    color_brightness = r + g + b

    # Define thresholds for classification. These are arbitrary and can be tuned.
    # Max brightness is 255 * 3 = 765.
    if color_brightness < 150:
        return "Adipoli Kadippam!"  # Very Strong
    elif 150 <= color_brightness < 300:
        return "Paakam Paal Chaya"  # Medium
    elif 300 <= color_brightness < 500:
        return "Entammo, Ithu Chaya Alla!" # Not Chai
    else:
        return "Paal Maathram"  # Mostly Milk


# --- Main Application ---
def main():
    # --- UI Setup ---
    st.title("☕ Chaya-o-Meter: The Useless Chai Strength Analyzer")
    st.write("Ever wondered if your chaya has the perfect strength? Point your camera at your cup of chaya, and let this highly 'scientific' tool tell you! For entertainment purposes only.")

    # Initialize session state for camera
    if 'run_camera' not in st.session_state:
        st.session_state.run_camera = False

    # --- Button Logic ---
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        if st.button("Start Chaya Analysis"):
            st.session_state.run_camera = True
    with col2:
        if st.button("Stop"):
            st.session_state.run_camera = False

    # --- Camera Feed Display ---
    frame_placeholder = st.empty()

    if st.session_state.run_camera:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            st.error("Cannot open camera. Please check permissions.")
        else:
            while st.session_state.run_camera:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture frame from camera.")
                    break

                # Get frame dimensions
                h, w, _ = frame.shape

                # --- Region of Interest (ROI) ---
                # Define a square ROI in the center of the frame
                roi_size = 100
                roi_x1 = int(w/2 - roi_size/2)
                roi_y1 = int(h/2 - roi_size/2)
                roi_x2 = int(w/2 + roi_size/2)
                roi_y2 = int(h/2 + roi_size/2)

                # Crop the ROI from the frame
                roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

                # --- Analysis ---
                # Calculate the average color of the ROI
                avg_color = cv2.mean(roi) # This is in BGR format

                # Get the prediction
                prediction = predict_chai_strength(avg_color)

                # --- Display on Frame ---
                # Draw the ROI rectangle on the main frame
                cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
                cv2.putText(frame, "Point your Chaya here", (roi_x1, roi_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Display the prediction text above the ROI
                text_size, _ = cv2.getTextSize(prediction, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                text_x = int(w/2 - text_size[0]/2)
                cv2.putText(frame, prediction, (text_x, roi_y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Convert the frame to RGB for Streamlit
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Display the frame in Streamlit
                frame_placeholder.image(frame, channels="RGB")

            # Release the camera resource
            cap.release()

    else:
        st.info("Click 'Start Chaya Analysis' to begin.")


if __name__ == "__main__":
    main()
