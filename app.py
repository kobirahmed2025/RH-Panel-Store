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
SENDER_PASSWORD = "spks mvxk flcc yfxd"

registration_store = {}


# রুট (Root) রাউট যোগ করা হলো
@app.route("/", methods=["GET"])
def home():
  return jsonify({
      "success": True,
      "message": "RH Panel Store API is running successfully!",
  })


@app.route("/api/register-request-otp", methods=["POST"])
def register_request_otp():
  data = request.get_json() or {}
  email = data.get("email")
  password = data.get("password")

  if not email or not password:
    return (
        jsonify(
            {"success": False, "message": "Email and password are required."}
        ),
        400,
    )

  otp = str(random.randint(100000, 999999))
  expires_at = time.time() + 600

  registration_store[email] = {
      "otp": otp,
      "expires_at": expires_at,
      "password": password,
  }

  message = MIMEMultipart("alternative")
  message["Subject"] = "RH Panel Store - Verify Your Email"
  message["From"] = SENDER_EMAIL
  message["To"] = email

  # একদম আধুনিক, বক্স ছাড়া প্রিমিয়াম কালারিং ডিজাইন এবং কপি বাটনসহ
  html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0f172a;
                margin: 0;
                padding: 0;
            }}
            .email-wrapper {{
                width: 100%;
                table-layout: fixed;
                background-color: #0f172a;
                padding: 40px 0;
            }}
            .email-content {{
                max-width: 480px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e1b4b 0%, #311045 100%);
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .email-header {{
                padding: 35px 30px 10px 30px;
                text-align: center;
            }}
            .email-header h1 {{
                font-size: 26px;
                margin: 0;
                font-weight: 800;
                letter-spacing: 1.5px;
                background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .email-body {{
                padding: 20px 30px 40px 30px;
                text-align: center;
            }}
            .email-body h2 {{
                color: #f3f4f6;
                font-size: 20px;
                margin-bottom: 10px;
            }}
            .email-body p {{
                color: #9ca3af;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 25px;
            }}
            .otp-code {{
                font-size: 38px;
                font-weight: bold;
                letter-spacing: 8px;
                color: #38bdf8;
                margin: 15px 0 25px 0;
            }}
            .copy-btn {{
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: #ffffff;
                text-decoration: none;
                padding: 12px 32px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 50px;
                display: inline-block;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
                letter-spacing: 0.5px;
            }}
            .footer-text {{
                margin-top: 35px;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center">
                    <table class="email-content" width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td class="email-header">
                                <h1>RH PANEL STORE</h1>
                            </td>
                        </tr>
                        <tr>
                            <td class="email-body">
                                <h2>Email Verification</h2>
                                <p>You're just one step away from finishing your account registration. Use the security code below:</p>
                                
                                <div class="otp-code">{otp}</div>

                                <!-- আধুনিক প্রিমিয়াম কপি বাটন -->
                                <a href="https://api.whatsapp.com/send?text={otp}" class="copy-btn" target="_blank">Copy Code</a>

                                <p class="footer-text">This code will expire in 10 minutes. If you didn't request this, please ignore this email.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
  message.attach(MIMEText(html, "html"))

  try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
      server.login(SENDER_EMAIL, SENDER_PASSWORD)
      server.sendmail(SENDER_EMAIL, email, message.as_string())
    return jsonify({"success": True, "message": "Verification code sent!"})
  except Exception as e:
    return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/register-verify-otp", methods=["POST"])
def register_verify_otp():
  data = request.get_json() or {}
  email = data.get("email")
  user_otp = data.get("otp")

  record = registration_store.get(email)

  if not record:
    return jsonify({"success": False, "message": "Request not found."}), 400

  if time.time() > record["expires_at"]:
    del registration_store[email]
    return jsonify({"success": False, "message": "OTP expired."}), 400

  if record["otp"] == str(user_otp):
    del registration_store.get(email)
    return jsonify({"success": True, "message": "Account created successfully!"})
  else:
    return jsonify({"success": False, "message": "Invalid OTP."}), 400


if __name__ == "__main__":
  app.run(debug=True, port=5000)
