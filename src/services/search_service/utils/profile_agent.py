import os
import json
import logging
from typing import List, Dict, Any
import httpx
from utils.file_handler import download_s3_files_to_temp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OR_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://cosolvent.app",
    "X-Title": "Cosolvent",
    "Content-Type": "application/json",
}


def generate_producer_description_with_ai(
    s3_urls: List[str],
    producer_profile: Dict[str, Any],
    example_markdown_output: str,
) -> str:
    """
    Generates an AI-powered markdown description of a producer by combining
    profile information and provided context.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is missing.")

    temp_dir = None
    try:
        # Download S3 files to a temporary local directory
        logger.info(f"Downloading files from S3 URLs: {s3_urls}")
        temp_dir, local_paths = download_s3_files_to_temp(s3_urls)
        logger.info(f"Downloaded {len(local_paths)} files to {temp_dir}")

        # Upload each file to OpenAI and capture file IDs
        # Convert producer profile to JSON string (convert non-serializable types to str)
        producer_profile_str = json.dumps(producer_profile, indent=2, default=str)

        # Prepare prompt messages
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional agricultural business consultant AI. "
                    "Given company information and file-based data (like brochures, certificates, or images), "
                    "write a well-structured, marketing-ready markdown profile. "
                    "Summarize the farm's operations, products, certifications, and export potential. "
                    "Use the given markdown sample as a stylistic reference. "
                    "Do NOT include raw file content, links, or file names — only useful insights from the files. "
                    "Ensure the profile is comprehensive, engaging, and suitable for a business audience."
                )
                
            },
            {
                "role": "user",
                "content": (
                    f"**Producer Profile (as JSON):**\n"
                    f"```json\n{producer_profile_str}\n```\n\n"
                    f"**Desired Output Format Example:**\n"
                    f"```markdown\n{example_markdown_output}\n```\n\n"
                    "Now generate the final producer profile. Feel free to add any relevant details and even sections."
                )
            }
        ]

        # Call OpenAI with retrieval tool and uploaded files
        logger.info("Calling OpenRouter API for profile description generation...")
        with httpx.Client(base_url="https://openrouter.ai/api/v1", headers=OR_HEADERS, timeout=60) as client:
            payload = {"model": "openai/gpt-5", "messages": prompt_messages, "temperature": 0.7}
            r = client.post("/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content") or ""
        return content.strip()

    except Exception as e:
        logger.error(f"An error occurred during AI generation: {e}")
        return f"Error generating description: {e}"
    finally:
        # Clean up the temporary directory and its contents
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
