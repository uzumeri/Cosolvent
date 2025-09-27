import logging
from typing import Optional
import aiohttp
import fitz  # PyMuPDF
import os
import asyncio
import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OR_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://cosolvent.app",
    "X-Title": "Cosolvent",
    "Content-Type": "application/json",
}

async def get_image_metadata_from_openrouter(image_url: str) -> str:
    """
    Analyzes an image from a URL using OpenRouter and returns a description.
    """
    try:
        logger.info(f"Analyzing image from URL: {image_url}")
        async with httpx.AsyncClient(base_url="https://openrouter.ai/api/v1", headers=OR_HEADERS, timeout=60) as client:
            payload = {
                "model": "openai/gpt-5",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What’s in this image? Describe it for a producer profile."},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                "max_tokens": 300,
            }
            r = await client.post("/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
        description = data.get("choices", [{}])[0].get("message", {}).get("content")
        return description.strip() if description else "No description generated."
    except Exception as e:
        logger.error(f"Error analyzing image with OpenRouter: {e}")
        raise

async def summarize_text_with_openrouter(text: str) -> Optional[str]:
    """
    Summarizes a given text using OpenRouter.
    """
    try:
        logger.info("Summarizing extracted text with OpenRouter...")
        max_chars = 15000  # Approx. 4k tokens
        truncated_text = text[:max_chars]

        async with httpx.AsyncClient(base_url="https://openrouter.ai/api/v1", headers=OR_HEADERS, timeout=60) as client:
            payload = {
                "model": "openai/gpt-5",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Summarize the following document content for a producer profile, "
                            "highlighting key details like certifications, farm practices, or product information."
                        ),
                    },
                    {"role": "user", "content": truncated_text},
                ],
            }
            r = await client.post("/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
        summary = data.get("choices", [{}])[0].get("message", {}).get("content")
        return summary.strip() if summary else None
    except Exception as e:
        logger.error(f"Error processing document with OpenRouter: {e}")
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

async def get_document_text_from_openrouter(file_url: str) -> Optional[str]:
    """
    Downloads a PDF, extracts its text, and generates a summary using OpenRouter.
    """
    try:
        logger.info(f"Processing document from URL: {file_url}")
        pdf_bytes = await download_file(file_url)
        extracted_text = extract_text_from_pdf(pdf_bytes)
        if not extracted_text:
            logger.warning(f"No text could be extracted from the document at {file_url}. Ensure the file is a valid document type of image or PDF.")
            return f"No text could be extracted from the document at {file_url}. Ensure the file is a valid document type of image or PDF."
        
        summary = await summarize_text_with_openrouter(extracted_text)
        return summary
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise
