# check_email_config.py
from config import Config

print("\n" + "="*60)
print("EMAIL CONFIGURATION CHECK")
print("="*60)
print(f"MAIL_SERVER: {Config.MAIL_SERVER}")
print(f"MAIL_PORT: {Config.MAIL_PORT}")
print(f"MAIL_USE_TLS: {Config.MAIL_USE_TLS}")
print(f"MAIL_USERNAME: {Config.MAIL_USERNAME}")
print(f"MAIL_PASSWORD: {'*' * 8 if Config.MAIL_PASSWORD else 'NOT SET'}")
print(f"MAIL_DEFAULT_SENDER: {Config.MAIL_DEFAULT_SENDER}")
print(f"MAIL_DEBUG: {Config.MAIL_DEBUG}")
print(f"APP_URL: {Config.APP_URL}")
print("="*60)

if not Config.MAIL_PASSWORD:
    print("\n⚠️ WARNING: MAIL_PASSWORD is not set!")
    print("   Emails will not be sent until you set the password.")
    print("   Get an app password from: https://myaccount.google.com/apppasswords")