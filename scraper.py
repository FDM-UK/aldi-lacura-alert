from bs4 import BeautifulSoup
import requests

url = "https://www.aldi.co.uk/products/specialbuys/health-and-beauty"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
products = soup.find_all('div', class_='product-tile')

# print(f"Found {len(products)} products")
# print(products[0])


lacura_found = False
for product in products:
    brand = product.find('div', class_='product-tile__brandname').text.strip()  # find the brandname div and get its text
    if 'lacura' in brand.lower():  # check the brand in lowercase
        print(f"Lacura product found: {product['title']}")
        lacura_found = True

if not lacura_found:
    print("No Lacura products found")