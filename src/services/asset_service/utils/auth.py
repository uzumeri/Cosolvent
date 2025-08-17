import httpx
from fastapi import Depends, HTTPException, Request, status
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)
AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL

async def get_current_user_email(request: Request) -> str:
    """
    Dependency to get the current user's email from the auth service.
    """
    session_token = request.cookies.get("better-auth.session_token")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: No session token provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                AUTH_SERVICE_URL,
                cookies={"better-auth.session_token": session_token},
            )
            
            if response.status_code == 200:
                user_data = response.json()
                email = user_data.get("user")["email"]
                return email
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated: Invalid session token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error verifying token with auth service."
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth service is unavailable: {exc}"
            )
