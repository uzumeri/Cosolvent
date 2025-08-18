import logging
from typing import Optional
import aiohttp
import fitz  # PyMuPDF
from openai import OpenAI
from src.core.config import settings
import asyncio

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def get_image_metadata_from_openai(image_url: str) -> str:
    """
    Analyzes an image from a URL using OpenAI's vision model and returns a description.
    """
    try:
        logger.info(f"Analyzing image from URL: {image_url}")
        # Use thread wrapper for synchronous OpenAI call
        def call_openai_image():
            return client.chat.completions.create(
                model="gpt-4o",
                messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What’s in this image? Describe it for a producer profile."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        response = await asyncio.to_thread(call_openai_image)
        description = response.choices[0].message.content
        return description.strip() if description else "No description generated."
    except Exception as e:
        logger.error(f"Error analyzing image with OpenAI: {e}")
        # Propagate exception to route for proper HTTP 500
        raise

async def summarize_text_with_openai(text: str) -> Optional[str]:
    """
    Asynchronously summarizes a given text using OpenAI's chat model offloaded to a thread to avoid blocking.
    """
    try:
        logger.info("Summarizing extracted text with OpenAI...")
        max_chars = 15000  # Approx. 4k tokens
        truncated_text = text[:max_chars]

        # Use thread wrapper for synchronous OpenAI call
        def call_openai_text():
            return client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Summarize the following document content for a producer profile, "
                            "highlighting key details like certifications, farm practices, or product information."
                        )
                    },
                    {"role": "user", "content": truncated_text}
                ]
            )

        response = await asyncio.to_thread(call_openai_text)
        summary = response.choices[0].message.content
        return summary.strip() if summary else None
    except Exception as e:
        logger.error(f"Error processing document with OpenAI: {e}")
        raise

async def download_file(url: str) -> bytes:
    """Downloads a file from a URL and returns its content as bytes."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download file: {resp.status}")
            return await resp.read()

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts all text from a PDF provided as bytes."""
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

async def get_document_text_from_openai(file_url: str) -> Optional[str]:
    """
    Downloads a PDF, extracts its text, and generates a summary using OpenAI.
    """
    try:
        logger.info(f"Processing document from URL: {file_url}")
        pdf_bytes = await download_file(file_url)
        extracted_text = extract_text_from_pdf(pdf_bytes)
        if not extracted_text:
            logger.warning(f"No text could be extracted from the document at {file_url}. Ensure the file is a valid document type of image or PDF.")
            return f"No text could be extracted from the document at {file_url}. Ensure the file is a valid document type of image or PDF."
        
        summary = await summarize_text_with_openai(extracted_text)
        return summary
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise