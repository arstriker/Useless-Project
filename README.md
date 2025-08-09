# Gemini Image Analyzer

This program is a Python script that uses the Google Gemini API to analyze a list of images. For each image, it provides a classification of the primary subject and a detailed descriptive comment.

## Features

- Analyzes images from both local file paths and URLs.
- Uses the `gemini-1.5-flash` multimodal model.
- Prompts the model to return a structured JSON response.
- Handles errors gracefully (e.g., invalid image paths, API failures).
- Outputs a clean JSON array of the results.

## Setup

Follow these steps to set up and run the program.

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install dependencies

The required Python libraries are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Configure your API Key

You need a Google Gemini API key to run this script.

1.  Obtain your API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  In the project directory, you will find a file named `.env`. Open it and replace `YOUR_API_KEY` with your actual key:

    ```
    GEMINI_API_KEY=YOUR_API_KEY
    ```

    The script uses the `python-dotenv` library to load this key securely.

## Usage

1.  **Edit the list of images:**
    Open the `image_analyzer.py` file and modify the `image_sources` list to include the local file paths or URLs of the images you want to analyze.

    ```python
    # image_analyzer.py

    # ...

    # List of image sources (can be local paths or URLs)
    image_sources = [
        "https://storage.googleapis.com/gweb-cloudblog-publish/images/GC_GENEM_1.max-2000x2000.jpg",
        "path/to/your/local/image.png",
        "https://example.com/another-image.jpg",
    ]

    # ...
    ```

2.  **Run the script:**

    ```bash
    python image_analyzer.py
    ```

## Output Format

The script will print a JSON array to the console. Each object in the array represents an analyzed image and contains the following fields:

-   `filename`: The original source of the image (path or URL).
-   `classification`: A brief classification of the image's primary subject.
-   `comment`: A detailed comment describing the image's content.

### Example Output:

```json
[
  {
    "filename": "https://storage.googleapis.com/gweb-cloudblog-publish/images/GC_GENEM_1.max-2000x2000.jpg",
    "classification": "Data Center",
    "comment": "An illustration of a modern data center with rows of server racks. The lighting is futuristic with blue and purple hues, and a person is standing in the aisle, interacting with one of the servers. The overall mood is high-tech and organized."
  }
]
```
