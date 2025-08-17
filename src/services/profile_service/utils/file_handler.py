import os
from pathlib import Path
import logging
from typing import List, Tuple
import tempfile
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_s3_files_to_temp(s3_urls: List[str]) -> Tuple[str, List[str]]:
    """
    Downloads files from public S3 URLs into a temporary directory
    and returns the directory path and a list of local file paths.
    """
    temp_dir = tempfile.mkdtemp()
    downloaded_file_paths = []
    logger.info(f"Created temporary directory: {temp_dir}")

    for url in s3_urls:
        try:
            # Extract filename from URL, handling query parameters
            filename = os.path.basename(url.split('?')[0])
            if not filename:
                # Create a fallback filename if parsing fails
                filename = f"downloaded_file_{len(downloaded_file_paths)}"
            
            local_filepath = os.path.join(temp_dir, filename)
            logger.info(f"Attempting to download: {url} to {local_filepath}")

            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            with open(local_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded_file_paths.append(local_filepath)
            logger.info(f"Successfully downloaded: {filename}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during download of {url}: {e}")

    return temp_dir, downloaded_file_paths

def download_and_process_s3_files(s3_urls: List[str]):
    """
    Downloads files from public S3 URLs into the `routes/templete_and_files` folder
    and returns their local file paths for LLM processing.
    """
    # Define destination directory inside routes/templete_and_files
    dest_dir = Path(__file__).parent.parent / 'templete_and_files'
    os.makedirs(dest_dir, exist_ok=True)
    downloaded_file_paths = []

    try:
        # Download each file into the permanent folder
        for url in s3_urls:
            try:
                # Extract filename from URL
                filename = os.path.basename(url.split('?')[0])
                if not filename: # Fallback if URL doesn't have a clear filename
                    filename = f"downloaded_file_{len(downloaded_file_paths)}"

                local_filepath = str(dest_dir / filename)
                logger.info(f"Attempting to download: {url} to {local_filepath}")

                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

                with open(local_filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_file_paths.append(local_filepath)
                logger.info(f"Successfully downloaded: {filename}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download {url}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred during download of {url}: {e}")

        if not downloaded_file_paths:
            logger.warning("No files were successfully downloaded.")

        # Return list of local file paths for LLM processing
        logger.info(f"Downloaded {len(downloaded_file_paths)} files to {dest_dir}")
        return downloaded_file_paths

    except Exception as e:
        logger.error(f"Error downloading files: {e}")
        return []

# function to read a markdown file and return its content
def read_markdown_file(file_path: str) -> str:
    """
    Reads a markdown file and returns its content as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Error reading markdown file {file_path}: {e}")
        return ""