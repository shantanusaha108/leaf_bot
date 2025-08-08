import cohere
from dotenv import load_dotenv
from PIL import Image
import base64
import os
from io import BytesIO
from logger import log_error

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "").strip()

if COHERE_API_KEY:
    co = cohere.Client(COHERE_API_KEY)
else:
    log_error("ConfigError", "Cohere API key not set")


def image_to_base64(image_path):
    """Convert image to base64 string."""
    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        log_error("ImageEncodingError", f"Failed to encode image: {e}")
        return None


def query_gemini(image=None, description=None, user_text=None, language="English"):
    """
    Simulates Gemini-like function but using Cohere.
    Accepts 'description' for backward compatibility with existing view code.
    If image is given, it will embed it and append description/user_text before sending to Chat.
    """
    if not COHERE_API_KEY:
        return "Error: Cohere API key not set."

    # Map description to user_text if needed
    if description and not user_text:
        user_text = description
    if not user_text:
        user_text = "No description provided"

    try:
        final_prompt = (
            f"You are a plant health expert. Identify the plant, "
            f"diagnose any diseases, explain the symptoms, and provide a solution. "
            f"Respond in {language}.\n\n"
        )

        if image:
            # Step 1: Convert to base64
            img_b64 = image_to_base64(image)
            if not img_b64:
                return "Error: Failed to process image."

            # Step 2: Generate embeddings (for potential search/future use)
            try:
                _ = co.embed(
                    model="embed-multilingual-v3.0",
                    input_type="image",
                    inputs=[img_b64]
                )
            except Exception as e:
                log_error("CohereEmbedError", f"Image embedding failed: {e}")

            # Step 3: Simple placeholder caption
            image_caption = "An image of a plant (automatically detected)."

            # Step 4: Merge caption + user text
            combined_text = f"{user_text}\n\nImage details: {image_caption}"
        else:
            combined_text = user_text

        # Step 5: Send to Cohere Chat
        response = co.chat(
            model="command-r-plus",
            message=final_prompt + combined_text
        )

        return response.text

    except Exception as e:
        log_error("CohereAPIError", f"Cohere request failed: {e}")
        return f"Error: {str(e)}"
