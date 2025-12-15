import json
import os
import requests
from flask import Blueprint, redirect, request, url_for
from flask_login import login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient
from app import db
from app.models import User

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(GOOGLE_CLIENT_ID)
google_auth_bp = Blueprint("google_auth", __name__)

@google_auth_bp.route("/google_login")
def google_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return "Google OAuth is not configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET.", 500
    
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as e:
        print(f"Google login error: {str(e)}")
        return "Error initiating Google login", 500

@google_auth_bp.route("/google_login/callback")
def google_callback():
    code = request.args.get("code")
    
    if not code:
        return "Missing authorization code", 400
    
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=request.base_url.replace("http://", "https://"),
            code=code,
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        userinfo = userinfo_response.json()
        
        if userinfo.get("email_verified"):
            users_email = userinfo["email"]
            users_name = userinfo.get("given_name", userinfo.get("name", ""))
        else:
            return "User email not verified by Google", 400
        
        user = User.query.filter_by(email=users_email).first()
        
        if not user:
            # Create new user with Google data
            user = User(username=users_name, email=users_email)
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for("main.dashboard"))
    
    except Exception as e:
        print(f"Google callback error: {str(e)}")
        return "Error processing Google login", 500

@google_auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
