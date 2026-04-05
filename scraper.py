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
    brand = product.find('div', class_='product-tile__brandname').text.strip()  # find the brandname div and get its text
    if 'lacura' in brand.lower():  # check the brand in lowercase
        print(f"Lacura product found: {product['title']}")
        lacura_found = True
        supabase.table('alert_log').insert({
            "product_name": product['title'],
            "recipient_count": 0
            }).execute()  # insert the product name into the alert_log table

if not lacura_found:
    print("No Lacura products found")