import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import re

# --- Constants ---
# TODO: User, please replace these placeholder URLs with direct links to your audio files (e.g., .mp3, .wav).
GOOD_CHAI_SONG_URL = "Upbeat Funk Background Music For Video [Royalty Free].mp3"  # e.g., "https://example.com/good_song.mp3"
BAD_CHAI_SONG_URL = "Sad Hamster Violin Meme (Full).mp3"  # e.g., "https://example.com/bad_song.mp3"

# --- Gemini Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=st.secrets["Apikey"])
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
    st.write("Is your chai a 5-star masterpiece or a 1-star disaster? Let the AI judge decide!")

    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = (0, "")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload a picture", label_visibility="collapsed", key="file_uploader")
    with col2:
        camera_photo = st.camera_input("Take a picture", label_visibility="collapsed", key="camera_input")

    image_to_analyze = None
    if uploaded_file:
        image_to_analyze = Image.open(uploaded_file)
    elif camera_photo:
        image_to_analyze = Image.open(camera_photo)

    if image_to_analyze:
        st.image(image_to_analyze, caption="The evidence for the judge.", use_container_width=True)
        # Run analysis when a new image is provided
        if "last_image" not in st.session_state or st.session_state.last_image != image_to_analyze:
            st.session_state.last_image = image_to_analyze
            rating, comment = analyze_image_with_gemini(image_to_analyze)
            st.session_state.analysis_result = (rating, comment)

    rating, comment = st.session_state.analysis_result
    if comment:
        if rating > 0:
            st.subheader(f"Rating: {'⭐' * rating}")
        st.success(f"The Judge says: {comment}")

        # Play audio based on the rating
        if rating >= 3:
            if GOOD_CHAI_SONG_URL:
                st.audio(GOOD_CHAI_SONG_URL, autoplay=True)
            else:
                st.info("Note: Add a URL for a 'good chai' song to hear music!")
        elif rating > 0:  # This covers 1 and 2 star ratings
            if BAD_CHAI_SONG_URL:
                st.audio(BAD_CHAI_SONG_URL, autoplay=True)
            else:
                st.info("Note: Add a URL for a 'bad chai' song to hear music!")


if __name__ == "__main__":
    main()
