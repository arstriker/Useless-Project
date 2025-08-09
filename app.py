import streamlit as st
import os
from dotenv import load_dotenv
import cv2
from PIL import Image
import google.generativeai as genai

# --- Gemini Configuration ---
# It's better to load and configure once at the start.
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key="AIzaSyBZLfcHVV1Yj-ZcInkllfCH05G1R_KbUBs")
else:
    # This will be handled gracefully in the UI.
    pass

def analyze_image_with_gemini(image: Image.Image):
    """
    Analyzes an image with the Gemini model to detect chai and generate a comment.
    """
    if not GEMINI_API_KEY:
        st.error("Aiyo, your GEMINI_API_KEY is missing lah. Create a .env file and put it there.")
        return "Cannot work without API key, boss."

    prompt = """
    You are a sarcastic Malayali friend. Look at this image. Your task is to identify if it contains 'Chai' (tea) and make a sarcastic comment in Manglish.

    Your response MUST follow this format exactly:
    `Detection: <result> | Comment: <comment>`

    - `<result>` must be either `Chai` or `Not Chai`.
    - `<comment>`:
        - If `<result>` is `Chai`, the comment must be a short, sarcastic, funny remark about the chai in Manglish.
        - If `<result>` is `Not Chai`, the comment must be a short, sarcastic, funny remark about what is in the picture instead.

    Example 1 (if it's chai):
    `Detection: Chai | Comment: Fuyoh, the color so kaw, you want to stay awake for one week is it?`

    Example 2 (if it's a cup of coffee):
    `Detection: Not Chai | Comment: Bro, that's coffee lah. Since when chai got foam art one? Don't play play.`

    Example 3 (if it's a cat):
    `Detection: Not Chai | Comment: This one is kucing, not chai. You want me to analyze its fluffiness ah?`

    Now, analyze the image I provide.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        with st.spinner("Aiyo, analyzing lah... My brain also need to warm up..."):
            response = model.generate_content([prompt, image])

            # Simple parsing based on the strict format requested in the prompt
            parts = response.text.strip().split('|')
            if len(parts) == 2 and 'Comment:' in parts[1]:
                comment = parts[1].replace('Comment:', '').strip()
                return comment
            else:
                # If the model doesn't follow the format, return the raw text.
                return f"Model went out of script, here's what it said: {response.text}"

    except Exception as e:
        st.error(f"Aiyo, something went wrong with Gemini: {e}")
        return "The AI is sleeping, try again later."

# --- Main Application ---
def main():
    # --- UI Setup ---
    st.title("🤖 Gemini Chaya-o-Meter ☕")
    st.write("Got chai? Or just some random liquid? Let's see what Gemini thinks. Upload a photo or use your camera. For entertainment purposes only, lah!")

    # Initialize session state variables
    if 'run_camera' not in st.session_state:
        st.session_state.run_camera = False
    if 'latest_frame' not in st.session_state:
        st.session_state.latest_frame = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = ""

    # --- Input Options ---
    uploaded_file = st.file_uploader("Upload a chaya picture:", type=["jpg", "jpeg", "png"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start/Stop Camera"):
            st.session_state.run_camera = not st.session_state.run_camera
            st.session_state.analysis_result = "" # Clear result when toggling camera

    # --- Placeholders ---
    image_placeholder = st.empty()
    comment_placeholder = st.empty()

    # --- Logic for Uploaded File ---
    if uploaded_file is not None:
        st.session_state.run_camera = False # Stop camera if a file is uploaded
        image = Image.open(uploaded_file)
        image_placeholder.image(image, caption="You uploaded this.", use_column_width=True)

        if st.button("Analyze Uploaded Image"):
            st.session_state.analysis_result = analyze_image_with_gemini(image)

    # --- Logic for Camera ---
    elif st.session_state.run_camera:
        with col2:
            if st.button("Analyze Camera Feed"):
                if st.session_state.latest_frame is not None:
                    # Convert BGR frame from OpenCV to RGB for PIL
                    frame_rgb = cv2.cvtColor(st.session_state.latest_frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    st.session_state.analysis_result = analyze_image_with_gemini(pil_image)
                else:
                    st.session_state.analysis_result = "No frame captured yet. Wait a second."

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Cannot open camera. Check permissions, maybe?")
        else:
            while st.session_state.run_camera:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture frame. Your camera is shy, maybe?")
                    break

                st.session_state.latest_frame = frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_placeholder.image(frame_rgb, channels="RGB", caption="Live Camera Feed")

            cap.release()
    else:
        image_placeholder.info("Your image or video will appear here.")
        st.session_state.latest_frame = None

    # Display the final comment if it exists
    if st.session_state.analysis_result:
        comment_placeholder.success(st.session_state.analysis_result)
    else:
        comment_placeholder.empty()

if __name__ == "__main__":
    main()
