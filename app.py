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
    elif 150 <= color_brightness < 400:
        return "Paakam Paal Chaya"  # Medium
    elif 400 <= color_brightness < 500:
        return "Entammo, Ithu Chaya Alla!" # Not Chai
    else:
        return "Paal Maathram"  # Mostly Milk


# --- Main Application ---
def analyze_image(frame):
    """
    Analyzes a single frame (or image) to determine chai strength.
    This function encapsulates the ROI selection, color analysis, and prediction.
    """
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

    # Apply a median blur to reduce the effect of bubbles/noise
    roi = cv2.medianBlur(roi, 15)

    # --- Analysis ---
    # Calculate the average color of the ROI
    avg_color = cv2.mean(roi) # This is in BGR format

    # Get the prediction
    prediction = predict_chai_strength(avg_color)

    # --- Display on Frame ---
    # Draw the ROI rectangle on the main frame
    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
    cv2.putText(frame, "Analyzed Area", (roi_x1, roi_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the prediction text above the ROI
    text_size, _ = cv2.getTextSize(prediction, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = int(w/2 - text_size[0]/2)
    cv2.putText(frame, prediction, (text_x, roi_y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    return frame


def main():
    # --- UI Setup ---
    st.title("☕ Chaya-o-Meter: The Useless Chai Strength Analyzer")
    st.write("Ever wondered if your chaya has the perfect strength? Point your camera at your cup of chaya, or upload a photo, and let this highly 'scientific' tool tell you! For entertainment purposes only.")

    # --- Image Upload ---
    uploaded_file = st.file_uploader("Choose a chaya image...", type=["jpg", "jpeg", "png"])

    # Initialize session state for camera
    if 'run_camera' not in st.session_state:
        st.session_state.run_camera = False

    # --- Button Logic ---
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        if st.button("Start Chaya Analysis"):
            st.session_state.run_camera = True
            # When starting camera, clear any uploaded file
            if uploaded_file is not None:
                uploaded_file = None
    with col2:
        if st.button("Stop"):
            st.session_state.run_camera = False

    # --- Main Logic ---
    frame_placeholder = st.empty()

    if uploaded_file is not None:
        # If an image is uploaded, process it
        st.session_state.run_camera = False # Ensure camera stops
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)

        # Analyze the image
        processed_image = analyze_image(image)

        # Convert to RGB and display
        processed_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(processed_image_rgb, channels="RGB", caption="Uploaded Chaya")

    elif st.session_state.run_camera:
        # If camera is running
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            st.error("Cannot open camera. Please check permissions.")
        else:
            while st.session_state.run_camera:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture frame from camera.")
                    break

                # Analyze the frame
                processed_frame = analyze_image(frame)

                # Convert the frame to RGB for Streamlit
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

                # Display the frame in Streamlit
                frame_placeholder.image(frame_rgb, channels="RGB")

            # Release the camera resource
            cap.release()

    else:
        # Default state
        st.info("Upload an image or click 'Start Chaya Analysis' to begin.")


if __name__ == "__main__":
    main()
