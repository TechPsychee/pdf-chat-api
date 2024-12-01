from google.auth.transport.requests import Request
import requests


def get_oauth_token():
    credentials = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/generative-language"],
    )

    credentials.refresh(Request())
    return credentials.token


def query_gemini_api(query_text):
    token = get_oauth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": query_text}]}]}
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


if __name__ == "__main__":
    query = "Explain how AI works"
    response = query_gemini_api(query)
    print(response)
