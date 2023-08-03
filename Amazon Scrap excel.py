import requests
import time
from bs4 import BeautifulSoup
from openpyxl import Workbook

def extract_product_data(url):
    product_data = []

    # Fetch the web page content
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    products = soup.find_all('div', class_='sg-row')

    for product in products:
        name_element = product.find('span', class_='a-size-medium')
        if name_element:
            product_name = name_element.text.strip()
        else:
            product_name = "N/A"

        price_element = product.find('span', class_='a-price')
        if price_element:
            product_price = price_element.find('span', class_='a-offscreen').text.strip()
        else:
            product_price = "N/A"

        rating_element = product.find('span', {'aria-label': True})
        if rating_element:
            product_rating = rating_element['aria-label'].split()[0]
        else:
            product_rating = "N/A"

        reviews_element = product.find('span', {'aria-label': True})
        if reviews_element:
            product_reviews = reviews_element['aria-label'].split()[-2]
        else:
            product_reviews = "N/A"

        url_element = product.find('a', class_='a-link-normal')
        if url_element:
            product_url = "https://www.amazon.in" + url_element['href']
        else:
            product_url = "N/A"

        # Additional data: ASIN, Product Description, and Manufacturer
        asin = "N/A"
        product_description = "N/A"
        manufacturer = "N/A"
        
        if product_url != "N/A" and product_url.startswith("https://www.amazon.in"):
            product_page = requests.get(product_url)
            if product_page.status_code == 200:
                product_soup = BeautifulSoup(product_page.content, 'html.parser')
                try:
                    asin = product_soup.find('th', string='ASIN').find_next('td').text.strip()
                except AttributeError:
                    pass

                try:
                    product_description = product_soup.find('div', id='productDescription').text.strip()
                except AttributeError:
                    pass

                try:
                    manufacturer = product_soup.find('th', string='Manufacturer').find_next('td').text.strip()
                except AttributeError:
                    pass

        product_data.append([product_name, product_price, product_rating, product_reviews, product_url, asin, product_description, manufacturer])

        # Add a delay of 1 second between each request
        time.sleep(1)

    return product_data

num_pages_to_scrape = 20
base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"

# Create a new Excel workbook and worksheet
workbook = Workbook()
worksheet = workbook.active

# Write the product data to the worksheet and print in the terminal
worksheet.append(["Product Name", "Product Price", "Rating", "Number of Reviews", "URL", "ASIN", "Product Description", "Manufacturer"])

try:
    for page_number in range(1, num_pages_to_scrape + 1):
        # Build the URL for each page
        url = base_url.format(page_number)
        
        # Call the function to extract product data from the page
        product_data = extract_product_data(url)
        
        # Write the product data to the worksheet and print in the terminal
        for product in product_data:
            worksheet.append(product)
            print("Product Name:", product[0])
            print("Product Price:", product[1])
            print("Rating:", product[2])
            print("Number of Reviews:", product[3])
            print("URL:", product[4])
            print("ASIN:", product[5])
            print("Product Description:", product[6])
            print("Manufacturer:", product[7])
            print("-----------------------------------")

        # Add a delay of 1 second between each request
        time.sleep(1)

    # Save the workbook to a file
    workbook.save("amazon_product.xlsx")
    print("Data saved to 'amazon_product.xlsx'")
except Exception as e:
    print("An error occurred:", str(e))
