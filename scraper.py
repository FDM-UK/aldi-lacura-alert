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

load_dotenv()

url_supabase = os.getenv("SUPABASE_URL")
key_supabase = os.getenv("SUPABASE_KEY")
supabase = create_client(url_supabase, key_supabase)

urls = ["https://www.aldi.co.uk/products/specialbuys/health-and-beauty", ]

thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

lacura_found = False
dupe_product = False
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
                supabase.table('alert_log').insert({
                    "product_name": product['title'],
                    "sale_date": sale_date,
                    "recipient_count": 0
                }).execute()
                print(f"Lacura product found: {product['title']} — {sale_date}")
            else:
                dupe_product = True
                print(f"Already alerted recently: {product['title']} — skipping")

if not  lacura_found and not dupe_product:
    print("No Lacura products found")
elif dupe_product and not lacura_found:
    print("Lacura products found but already alerted recently")