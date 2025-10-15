from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, HTTPException
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# OAuth configuration
config = Config('.env')
oauth = OAuth(config)

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

async def get_oauth_user(request: Request, provider: str) -> Optional[dict]:
    """Get user information from OAuth provider."""
    try:
        token = await oauth.authorize_access_token(request)
        if provider == 'google':
            user_info = await oauth.google.parse_id_token(request, token)
            return {
                'id': user_info.get('sub'),
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', ''),
                'provider': 'google'
            }
        elif provider == 'github':
            resp = await oauth.github.get('user', token=token)
            user_info = resp.json()
            return {
                'id': str(user_info.get('id')),
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('avatar_url', ''),
                'provider': 'github'
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None 