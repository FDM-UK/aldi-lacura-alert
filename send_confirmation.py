"""Set up subscriber confirmation email template and 
send confirmation email to new subscribers.
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()

url_supabase = os.getenv("SUPABASE_URL")
key_supabase = os.getenv("SUPABASE_KEY")
brevo_api_key = os.getenv("BREVO_API_KEY")
brevo_sender_email = os.getenv("BREVO_SENDER_EMAIL")

supabase = create_client(url_supabase, key_supabase)

def send_confirmation_email(recipient_email, token):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = brevo_api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    confirmation_url = f"https://lacuraalerts.co.uk/confirm?token={token}"

    subject = "Confirm your subscription to Lacura Alerts"
    content = f"Thank you for subscribing to Lacura Alerts! Please confirm your subscription by clicking the link below:\n\n{confirmation_url}\n\nIf you did not subscribe, please ignore this email."

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": recipient_email}], 
        sender={"email": brevo_sender_email, "name": "Lacura Alerts"},
        subject=subject,
        text_content=content
    ) 
    api_instance.send_transac_email(email)  

pending = supabase.table('subscribers')\
    .select('email, token')\
    .eq('confirmed', False)\
    .eq('confirmation_sent', False)\
    .execute()

for subscriber in pending.data:
    send_confirmation_email(
        subscriber['email'],
          subscriber['token']
          )
    supabase.table('subscribers')\
        .update({'confirmation_sent': True})\
        .eq('email', subscriber['email'])\
        .execute()
    print(f'Confirmation sent to {subscriber["email"]}')

if not pending.data:
    print('No pending confirmations')