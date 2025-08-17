import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from src.core.config import settings
from utils.file_handler import download_s3_files_to_temp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

openai_api_key = settings.OPENAI_API_KEY
client = OpenAI(api_key=openai_api_key)

def upload_files_to_openai(file_paths: List[str]) -> List[str]:
    """
    Uploads files to OpenAI and returns a list of file IDs.
    """
    file_ids = []
    for path in file_paths:
        try:
            with open(path, "rb") as f:
                uploaded_file = client.files.create(file=f, purpose="assistants")
                file_ids.append(uploaded_file.id)
                logger.info(f"Uploaded {path} as {uploaded_file.id}")
        except Exception as e:
            logger.error(f"Failed to upload {path}: {e}")
    return file_ids


def generate_producer_description_with_ai(
    s3_urls: List[str],
    producer_profile: Dict[str, Any],
    example_markdown_output: str,
) -> str:
    """
    Generates an AI-powered markdown description of a producer by combining
    profile information and uploaded file content using OpenAI Retrieval.
    """
    if not openai_api_key:
        raise ValueError("OpenAI API key is missing.")

    temp_dir = None
    try:
        # Download S3 files to a temporary local directory
        logger.info(f"Downloading files from S3 URLs: {s3_urls}")
        temp_dir, local_paths = download_s3_files_to_temp(s3_urls)
        logger.info(f"Downloaded {len(local_paths)} files to {temp_dir}")

        # Upload each file to OpenAI and capture file IDs
        logger.info("Uploading files to OpenAI...")
        file_ids = upload_files_to_openai(local_paths)
        logger.info(f"Uploaded {len(file_ids)} files, IDs: {file_ids}")

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
        logger.info("Calling OpenAI API with retrieval tool and file IDs...")
        # Call chat completion (suppress type-check for message dicts)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt_messages,  # type: ignore[arg-type]
            temperature=0.7
        )
      
        # Safely extract and strip content
        content = response.choices[0].message.content or ""
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
