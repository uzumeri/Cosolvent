import logging
from typing import Tuple

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


async def create_farmer_account(name: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Create a PRODUCER account in the auth service using email+password signup.

    Returns (ok, message). If ok=False, message contains error detail.
    """
    if not name:
        name = email.split("@")[0]  # use email prefix as name if not provided
    payload = {
        "name": name,
        "email": email,
        "userType": "PRODUCER",
        "password": password,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(settings.AUTH_SIGNUP_URL, json=payload)
            if resp.status_code in (200, 201):
                return True, "created"
            # try to extract error
            try:
                data = resp.json()
            except Exception:
                data = {"detail": resp.text}
            msg = data.get("message") or data.get("detail") or f"status={resp.status_code}"
            logger.error("Auth signup failed for %s: %s", email, msg)
            return False, msg
    except httpx.RequestError as e:
        logger.exception("Auth signup request error for %s: %s", email, e)
        return False, str(e)

