import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import httpx
import logging

logger = logging.getLogger(__name__)


def get_oauth_token():
    credentials = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/generative-language"],
    )
    credentials.refresh(Request())
    return credentials.token


async def chat_with_pdf(pdf_id, query):
    api_url = os.getenv(
        "GEMINI_API_URL",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
    )
    token = get_oauth_token()

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": f"PDF ID: {pdf_id}\nQuery: {query}"}]}]}

    try:
        logger.info(f"Payload: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, headers=headers)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")
            response.raise_for_status()
            return (
                response.json()
                .get("contents", [{}])[0]
                .get("parts", [{}])[0]
                .get("text", "No response from Gemini API.")
            )
    except httpx.RequestError as e:
        logger.error(f"Error communicating with Gemini API: {e}")
        raise Exception(f"Error communicating with Gemini API: {e}")
