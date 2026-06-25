from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


def create_flow(client_id: str, client_secret: str, redirect_uri: str, scopes): #Oauth Builder
    """Create OAuth flow for Google authentication."""
    if not client_id or not client_secret:
        raise ValueError("Google OAuth credentials not configured")

    return Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=scopes,
    )


def get_user_info(credentials):
    """Get user information from Google."""
    try:
        service = build("oauth2", "v2", credentials=credentials)
        return service.userinfo().get().execute()
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None
