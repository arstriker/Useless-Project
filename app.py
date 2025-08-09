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


# --- Reusable Analysis Function ---
def analyze_image(image_bgr):
    """
    Analyzes a static image (BGR format), annotates it with the prediction,
    and returns the annotated image and the prediction string.

    Args:
        image_bgr (np.array): The image to analyze in BGR format.

    Returns:
        tuple: A tuple containing:
               - annotated_image (np.array): The image with the prediction text.
               - prediction (str): The prediction string.
    """
    # Make a copy to avoid modifying the original image
    annotated_image = image_bgr.copy()

    # Calculate the average color of the entire image
    avg_color = cv2.mean(annotated_image)

    # Get the prediction
    prediction = predict_chai_strength(avg_color)

    # --- Annotate the image ---
    h, w, _ = annotated_image.shape
    text = f"Analysis: {prediction}"
    font_scale = min(w, h) / 600
    font_thickness = 2 if font_scale > 0.5 else 1
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

    # Position text at the top center
    text_x = int((w - text_size[0]) / 2)
    text_y = int(h * 0.1)

    # Add text to the copied image
    cv2.putText(annotated_image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    return annotated_image, prediction


# --- Main Application ---
def main():
    # --- UI Setup ---
    st.title("☕ Chaya-o-Meter: The Useless Chai Strength Analyzer")
    st.write("Let this highly 'scientific' tool analyze your chaya from a snapshot or an uploaded image. For entertainment purposes only.")

    # --- UI Tabs for Mode Selection ---
    tab1, tab2 = st.tabs(["Take a Snapshot", "Upload an Image"])

    with tab1:
        st.header("Analyze Chaya from a Snapshot")
        img_file_buffer = st.camera_input("Point the camera at your chaya and take a photo!", key="chaya_camera")

        if img_file_buffer is not None:
            # Read the image data from the buffer into a numpy array
            file_bytes = np.asarray(bytearray(img_file_buffer.read()), dtype=np.uint8)
            # Decode the numpy array into an OpenCV image (BGR format)
            image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image_bgr is not None:
                # Analyze the image using our reusable function
                annotated_image_bgr, prediction = analyze_image(image_bgr)

                # Display the result
                st.subheader(f"Analysis Result: {prediction}")

                # Convert the annotated image from BGR to RGB for Streamlit display
                annotated_image_rgb = cv2.cvtColor(annotated_image_bgr, cv2.COLOR_BGR2RGB)
                st.image(annotated_image_rgb, caption="Your Analyzed Snapshot", use_column_width=True)
            else:
                st.error("Could not process the camera snapshot. Please try again.")

    with tab2:
        st.header("Analyze Chaya from an Uploaded Image")
        uploaded_file = st.file_uploader("Choose an image of your chaya...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Read the uploaded image file into a numpy array
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            # Decode the numpy array into an OpenCV image (BGR format)
            image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image_bgr is not None:
                # Analyze the image using our reusable function
                annotated_image_bgr, prediction = analyze_image(image_bgr)

                # Display the result
                st.subheader(f"Analysis Result: {prediction}")

                # Convert the annotated image from BGR to RGB for Streamlit display
                annotated_image_rgb = cv2.cvtColor(annotated_image_bgr, cv2.COLOR_BGR2RGB)
                st.image(annotated_image_rgb, caption="Your Analyzed Chaya", use_column_width=True)
            else:
                st.error("Could not decode the image. Please try another file.")


if __name__ == "__main__":
    main()
