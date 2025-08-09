import streamlit as st
import os
from dotenv import load_dotenv
import cv2
from PIL import Image
import google.generativeai as genai
import re

# --- Gemini Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key="AIzaSyBZLfcHVV1Yj-ZcInkllfCH05G1R_KbUBs")
else:
    pass


def analyze_image_with_gemini(image: Image.Image):
    """
    Analyzes an image with Gemini, returning a rating and a comment.
    """
    if not GEMINI_API_KEY:
        st.error("Aiyo, your GEMINI_API_KEY is missing Daa. Create a .env file and put it there.")
        return 0, "Cannot work without API key, boss."

    prompt = """
    You are a sarcastic Malayali friend from Kerala, and you are now a "Chai Judge". Your task is to analyze the image, identify if it contains 'Chai' (tea), and then rate it and make a comment.

    Your response MUST follow this format exactly:
    `Rating: <rating_number> | Comment: <comment>`

    - If the image does not contain Chai, the rating must be `0`.
    - If the image contains Chai, `<rating_number>` must be a number from 1 to 5.

    Your `<comment>` must be in Manglish (mostly English with some Malayalam words) and its tone MUST depend on the rating:
    - **Rating 0 (Not Chai):** Make a sarcastic comment about what's in the picture instead of chai.
    - **Rating 1-2 (Bad Chai):** Mercilessly roast the chai. Be funny and brutal.
    - **Rating 3 (Average Chai):** Be encouraging. Say something like "Not bad, but you can improve."
    - **Rating 4-5 (Good Chai):** Give it a funny and enthusiastic compliment.

    Example 1 (Good Chai):
    `Rating: 5 | Comment: Adipoli! This is the king of all chayas. The color, the texture... perfect! I would drink this all day.`

    Example 2 (Bad Chai):
    `Rating: 1 | Comment: Eda, what is this? It looks like you just washed your hands in this cup. Don't ever make chai again.`

    Example 3 (Not Chai):
    `Rating: 0 | Comment: My friend, this is a picture of a laptop. Are you trying to make me rate its battery life?`

    Now, analyze the image I provide and give me your rating and comment.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        with st.spinner("Aiyo, analyzing daa... Let the judging begin..."):
            response = model.generate_content([prompt, image])

            # Use regex for more robust parsing
            match = re.search(r"Rating:\s*(\d+)\s*\|\s*Comment:\s*(.*)", response.text, re.DOTALL)
            if match:
                rating = int(match.group(1))
                comment = match.group(2).strip()
                return rating, comment
            else:
                return 0, f"Model went out of script, here's what it said: {response.text}"

    except Exception as e:
        st.error(f"Aiyo, something went wrong with Gemini: {e}")
        return 0, "The AI judge is sleeping, try again later."


# --- Main Application ---
def main():
    st.title("🤖 Chai-o-Meter ☕")
    st.write("Is your chai a 5-star masterpiece or a 1-star disaster? Let the Ai judge decide!")

    if 'run_camera' not in st.session_state:
        st.session_state.run_camera = False
    if 'latest_frame' not in st.session_state:
        st.session_state.latest_frame = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = (0, "")  # Store as a tuple (rating, comment)

    uploaded_file = st.file_uploader("Upload a chaya picture:", type=["jpg", "jpeg", "png"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start/Stop Camera"):
            st.session_state.run_camera = not st.session_state.run_camera
            st.session_state.analysis_result = (0, "")

    image_placeholder = st.empty()
    rating_placeholder = st.empty()
    comment_placeholder = st.empty()

    if uploaded_file is not None:
        st.session_state.run_camera = False
        image = Image.open(uploaded_file)
        image_placeholder.image(image, caption="The evidence.", use_container_width=True)

        if st.button("Judge this Chai!"):
            st.session_state.analysis_result = analyze_image_with_gemini(image)

    elif st.session_state.run_camera:
        with col2:
            if st.button("Judge this Chai from Camera!"):
                if st.session_state.latest_frame is not None:
                    frame_rgb = cv2.cvtColor(st.session_state.latest_frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    st.session_state.analysis_result = analyze_image_with_gemini(pil_image)
                else:
                    st.session_state.analysis_result = (0, "No frame captured yet. Wait a second.")

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
        image_placeholder.info("Your image or video will appear here for judgment.")
        st.session_state.latest_frame = None

    rating, comment = st.session_state.analysis_result
    if comment:
        if rating > 0:
            rating_placeholder.subheader(f"Rating: {'⭐' * rating}")
        else:
            rating_placeholder.empty()
        comment_placeholder.success(f"The Judge says: {comment}")
    else:
        rating_placeholder.empty()
        comment_placeholder.empty()


if __name__ == "__main__":
    main()
