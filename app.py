import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# আপনার জেনারেট করা অ্যাপ পাসওয়ার্ড
SENDER_EMAIL = "n76167138@gmail.com"
SENDER_PASSWORD = "hcvf zezn jkgx srtp"

registration_store = {}

@app.route('/api/register-request-otp', methods=['POST'])
def register_request_otp():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    otp = str(random.randint(100000, 999999))
    expires_at = time.time() + 600

    registration_store[email] = {
        "otp": otp,
        "expires_at": expires_at,
        "password": password
    }

    message = MIMEMultipart("alternative")
    message["Subject"] = "RH Panel Store - Verify your email"
    message["From"] = SENDER_EMAIL
    message["To"] = email

    html = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 30px;">
        <div style="max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <h2 style="color: #4f46e5; text-align: center; margin-bottom: 20px;">RH Panel Store</h2>
            <h3 style="color: #1f2937;">Verify your email</h3>
            <p style="color: #4b5563; font-size: 14px;">Use this code to finish creating your account.</p>
            <div style="background: #eef2ff; border-radius: 8px; padding: 20px; text-align: center; margin: 25px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #4f46e5;">{otp}</span>
            </div>
        </div>
    </div>
    """
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message.as_string())
        return jsonify({"success": True, "message": "Verification code sent!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/register-verify-otp', methods=['POST'])
def register_verify_otp():
    data = request.get_json() or {}
    email = data.get('email')
    user_otp = data.get('otp')

    record = registration_store.get(email)

    if not record:
        return jsonify({"success": False, "message": "Request not found."}), 400

    if time.time() > record['expires_at']:
        del registration_store[email]
        return jsonify({"success": False, "message": "OTP expired."}), 400

    if record['otp'] == str(user_otp):
        del registration_store[email]
        return jsonify({"success": True, "message": "Account created successfully!"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
