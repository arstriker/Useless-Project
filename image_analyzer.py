import os
import json
import requests
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def configure_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")
    genai.configure(api_key=api_key)

def get_image_from_source(source):
    """
    Opens an image from a local file path or a URL.
    Returns a PIL Image object or None if the source is invalid.
    """
    try:
        if source.startswith(('http://', 'https://')):
            headers = {'User-Agent': 'GeminiImageAnalyzer/1.0 (https://example.com/bot; bot@example.com)'}
            response = requests.get(source, headers=headers)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(source)
        return image
    except Exception as e:
        print(f"Error loading image from {source}: {e}")
        return None

def analyze_image_with_gemini(image, prompt_text):
    """
    Analyzes an image with the Gemini model and returns the response.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt_text, image])
        return response.text
    except Exception as e:
        return f"Error during API call: {e}"

def main():
    """
    Main function to process a list of images and print the analysis.
    """
    configure_gemini()

    # The prompt is designed to get a JSON object as a response.
    prompt = """
    Analyze the provided image and respond with a JSON object containing two keys:
    1. "classification": A brief, one or two-word classification of the primary subject.
    2. "comment": A detailed, descriptive comment about the image's content, including objects, setting, and mood.

    Do not include any text outside of the JSON object in your response.
    """

    # List of image sources (can be local paths or URLs)
    image_sources = [
        "https://upload.wikimedia.org/wikipedia/commons/b/b1/VAN_CAT.png",
        # Add more image paths or URLs here
        # e.g., "path/to/your/image.jpg",
    ]

    results = []
    for source in image_sources:
        print(f"Processing image: {source}...")
        image = get_image_from_source(source)
        if image:
            analysis_text = analyze_image_with_gemini(image, prompt)
            try:
                # Clean the response to extract only the JSON part.
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_string = analysis_text[json_start:json_end]
                    analysis_json = json.loads(json_string)
                    result = {
                        "filename": source,
                        "classification": analysis_json.get("classification", "N/A"),
                        "comment": analysis_json.get("comment", "N/A")
                    }
                else:
                    # If no JSON object is found, raise an error to be caught below.
                    raise json.JSONDecodeError("No JSON object found in the response.", analysis_text, 0)
            except json.JSONDecodeError:
                result = {
                    "filename": source,
                    "classification": "Error",
                    "comment": f"Failed to parse JSON from response: {analysis_text}"
                }
            results.append(result)

    # Print the final results as a JSON array
    print("\n--- Analysis Complete ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
