import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import re

# --- Gemini Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key="AIzaSyBZLfcHVV1Yj-ZcInkllfCH05G1R_KbUBs")
else:
    # This will be handled gracefully in the UI.
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
    st.title("🤖 Gemini Chaya-o-Meter ☕")
    st.write("Is your chai a 5-star masterpiece or a 1-star disaster? Let the Malayali judge decide!")

    # --- Input Options ---
    # We can use columns to place them side-by-side for a cleaner look.
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload a picture", label_visibility="collapsed", key="file_uploader")
    with col2:
        camera_photo = st.camera_input("Take a picture", label_visibility="collapsed", key="camera_input")

    # --- Analysis Trigger ---
    # The logic is now much simpler. We process whichever input was last used.
    image_to_analyze = None
    if uploaded_file is not None:
        # To prevent re-running analysis on every interaction after upload,
        # we can use a session state flag.
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.last_uploaded_file = uploaded_file.name
            st.session_state.last_camera_photo = None
            image_to_analyze = Image.open(uploaded_file)
            st.session_state.image_to_display = image_to_analyze

    if camera_photo is not None:
        if "last_camera_photo" not in st.session_state or st.session_state.last_camera_photo != camera_photo.getvalue():
            st.session_state.last_camera_photo = camera_photo.getvalue()
            st.session_state.last_uploaded_file = None
            image_to_analyze = Image.open(camera_photo)
            st.session_state.image_to_display = image_to_analyze

    # --- Display and Analysis ---
    if "image_to_display" in st.session_state and st.session_state.image_to_display is not None:
        st.image(st.session_state.image_to_display, caption="The evidence for the judge.", use_container_width=True)

        # If a new image has been provided, run the analysis.
        if image_to_analyze:
            rating, comment = analyze_image_with_gemini(image_to_analyze)
            st.session_state.analysis_result = (rating, comment)

    # Display the result from session state.
    if "analysis_result" in st.session_state:
        rating, comment = st.session_state.analysis_result
        if comment:
            if rating > 0:
                st.subheader(f"Rating: {'⭐' * rating}")
            st.success(f"The Judge says: {comment}")


if __name__ == "__main__":
    main()
