"""
Scrapes the Aldi health and beauty Special Buys page
and checks for Lacura products.
"""


from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()

url_supabase = os.getenv("SUPABASE_URL")
key_supabase = os.getenv("SUPABASE_KEY")
brevo_api_key = os.getenv("BREVO_API_KEY")
brevo_sender_email = os.getenv("BREVO_SENDER_EMAIL")
supabase = create_client(url_supabase, key_supabase)

def send_alert_email(recipient_email, new_products, token):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = brevo_api_key
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    unsubscribe_url = f"https://lacuraalerts.co.uk/unsubscribe?token={token}"

    subject = "Lacura is in Aldi Special Buys!"
    product_lines = "\n".join([f"- {p['name']} — {p['sale_date']}" for p in new_products])
    content = f"Good news! We found Lacura products in this week's Aldi Special Buys listings:\n\n{product_lines}\n\nHead to your nearest Aldi!\n\nTo unsubscribe from these alerts, click here: {unsubscribe_url}\n\n---\nIf you find this service useful, you can buy me a coffee: https://ko-fi.com/lacura_alerts"    
    
    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": recipient_email}],
        sender={"email": brevo_sender_email, "name": "Lacura Alerts"},
        subject=subject,
        text_content=content
    )
    
    api_instance.send_transac_email(email)

urls = ["https://www.aldi.co.uk/products/specialbuys/health-and-beauty", ]

thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()


lacura_found = False
dupe_product = False
new_products = []

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', class_='product-tile')

    for product in products:
        brand = product.find('div', class_='product-tile__brandname').text.strip()
        if 'lacura' in brand.lower():
            badge = product.find('div', class_='base-label--info')
            if badge:
                sale_date = badge.text.strip()
            else:
                sale_date = "In Store Now"

            existing = supabase.table('alert_log')\
                .select('id')\
                .eq('product_name', product['title'])\
                .eq('sale_date', sale_date)\
                .gte('sent_at', thirty_days_ago)\
                .execute()

            if not existing.data:
                lacura_found = True
                new_products.append({
                    'name': product['title'],
                    'sale_date': sale_date
                })
                supabase.table('alert_log').insert({
                    "product_name": product['title'],
                    "sale_date": sale_date,
                    "recipient_count": 0
                }).execute()
            else:
                dupe_product = True
                print(f"Already alerted recently: {product['title']} — skipping")

if new_products:
    subscribers = supabase.table('subscribers')\
        .select('email, token')\
        .eq('confirmed', True)\
        .execute()

    recipient_count = len(subscribers.data)

    for subscriber in subscribers.data:
        send_alert_email(
            subscriber['email'],
            new_products,
            subscriber['token']
        )

    # Update recipient count for all new alerts
    for p in new_products:
        supabase.table('alert_log')\
            .update({"recipient_count": recipient_count})\
            .eq('product_name', p['name'])\
            .execute()

    print(f"Sent alert to {recipient_count} subscribers")
    
if not lacura_found and not dupe_product:
    print("No Lacura products found")
elif dupe_product and not lacura_found:
    print("Lacura products found but already alerted recently")