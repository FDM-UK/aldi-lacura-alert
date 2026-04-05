"""
Scrapes the Aldi health and beauty Special Buys page
and checks for Lacura products.
"""


from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url_supabase = os.getenv("SUPABASE_URL")
key_supabase = os.getenv("SUPABASE_KEY")
supabase = create_client(url_supabase, key_supabase)

url = "https://www.aldi.co.uk/products/specialbuys/health-and-beauty"
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
products = soup.find_all('div', class_='product-tile')

lacura_found = False
for product in products:
    brand = product.find('div', class_='product-tile__brandname').text.strip()
    if 'lacura' in brand.lower():
        badge = product.find('div', class_='base-label--info')
        if badge:
            sale_date = badge.text.strip()
        else:
            sale_date = "In Store Now"
        print(f"Lacura product found: {product['title']} — {sale_date}")
        lacura_found = True
        supabase.table('alert_log').insert({
            "product_name": product['title'],
            "sale_date": sale_date,
            "recipient_count": 0
        }).execute()

if not lacura_found:
    print("No Lacura products found")