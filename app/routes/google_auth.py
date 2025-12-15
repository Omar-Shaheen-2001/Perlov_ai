import json
import os
import requests
from flask import Blueprint, redirect, request, url_for, flash
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
        flash("خدمة Google غير مفعّلة", "error")
        return redirect(url_for('auth.login'))
    
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL, timeout=5).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        redirect_uri = request.base_url + "callback"
        if request.host.endswith(".replit.dev"):
            redirect_uri = redirect_uri.replace("http://", "https://")
        
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as e:
        print(f"[GOOGLE] Login init error: {e}", flush=True)
        flash("خطأ في الاتصال بـ Google", "error")
        return redirect(url_for('auth.login'))

@google_auth_bp.route("/google_login/callback")
def google_callback():
    try:
        error = request.args.get("error")
        if error:
            flash("تم رفض الطلب من Google", "error")
            return redirect(url_for('auth.login'))
        
        code = request.args.get("code")
        if not code:
            flash("خطأ: رمز المصادقة غير موجود", "error")
            return redirect(url_for('auth.login'))
        
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL, timeout=5).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        redirect_uri = request.base_url.rsplit("/callback", 1)[0] + "/callback"
        if request.host.endswith(".replit.dev"):
            redirect_uri = redirect_uri.replace("http://", "https://")
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code,
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
            timeout=10
        )
        
        if token_response.status_code != 200:
            flash("فشل الحصول على رمز المصادقة من Google", "error")
            return redirect(url_for('auth.login'))
        
        token_json = token_response.json()
        client.parse_request_body_response(json.dumps(token_json))
        
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, timeout=5)
        
        if userinfo_response.status_code != 200:
            flash("فشل في الحصول على معلومات المستخدم", "error")
            return redirect(url_for('auth.login'))
        
        userinfo = userinfo_response.json()
        
        if not userinfo.get("email_verified"):
            flash("البريد الإلكتروني غير مُتحقق منه في Google", "error")
            return redirect(url_for('auth.login'))
        
        email = userinfo["email"]
        name = userinfo.get("given_name", userinfo.get("name", ""))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email)
            user.set_password("oauth_user")
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for("dashboard.index"))
    
    except Exception as e:
        print(f"[GOOGLE] Callback error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        flash("حدث خطأ في تسجيل الدخول", "error")
        return redirect(url_for('auth.login'))

@google_auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
