# # scraping/amazon_scraper.py
import requests
from bs4 import BeautifulSoup
from product_hunt.models import Website, Product

# class AmazonScraper:
#     def __init__(self, url):
#         self.url = url
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }

#     def scrape(self):
#         response = requests.get(self.url, headers=self.headers)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         website, created = Website.objects.get_or_create(name='Amazon', url=self.url)

#         for item in soup.select('.s-main-slot .s-result-item'):
#             name = item.select_one('h2 a span').text if item.select_one('h2 a span') else 'N/A'
#             price = item.select_one('.a-price-whole').text if item.select_one('.a-price-whole') else 'N/A'
#             reviews = item.select_one('.a-size-base').text if item.select_one('.a-size-base') else 'N/A'

#             Product.objects.create(
#                 name=name,
#                 price=price,
#                 reviews=reviews,
#                 website=website
#             )


import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import random
import re

class AmazonScraper:

    def __init__(self, base_url, max_pages=5):
        """
        Initializes an instance of the AmazonScraper class.

        Args:
            base_url (str): The base URL of the Amazon website.
            max_pages (int, optional): The maximum number of pages to scrape. Defaults to 5.

        Returns:
            None

        Initializes the instance variables of the AmazonScraper class with the provided base URL and maximum number of pages.
        Sets the user agent and timeout for making HTTP requests.
        Configures the logging module to log messages at the INFO level.
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
            # Add more user agents here
        ]
        self.TIMEOUT = 10
        logging.basicConfig(level=logging.INFO)

    def fetch_html(self, url):
        """
        Fetches the HTML content of a webpage using the provided URL.

        Parameters:
            url (str): The URL of the webpage to fetch.

        Returns:
            str or None: The HTML content of the webpage if the request is successful, None otherwise.
        """
        try:
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.amazon.com/"
            }
            response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch webpage: {url}. Exception: {str(e)}")
            return None

    def parse_html(self, html_text):
        """
        Parses the given HTML text using the BeautifulSoup library and returns the parsed HTML object.

        Parameters:
            html_text (str): The HTML text to be parsed.

        Returns:
            BeautifulSoup: The parsed HTML object.
        """
        try:
            return BeautifulSoup(html_text, 'html.parser')
        except Exception as e:
            logging.error(f"Error parsing HTML: {str(e)}")
            return None


    def extract_product_name(self, soup):
        """
        Extracts the product name from the given BeautifulSoup object.

        Parameters:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            str: The product name extracted from the HTML content. If the product name cannot be found, it returns 'N/A'.

        """ 
        try:
            name = soup.select_one('h2 a span').text if soup.select_one('h2 a span') else None
            return name
        except Exception as e:
            logging.error(f"Error extracting product name: {str(e)}")
            return None

    def extract_product_price(self, soup):
        """
        Extracts the price of a product from the given BeautifulSoup object.

        Parameters:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            str: The price of the product. If the price cannot be found, it returns 'N/A'.
        """
        try:
            price = soup.select_one('.a-price-whole').text if soup.select_one('.a-price-whole') else None
            return price
        except Exception as e:
            logging.error(f"Error extracting product price: {str(e)}")
            return None

    def extract_product_reviews(self, soup):
        """
        Extracts the product reviews from the given BeautifulSoup object.

        Parameters:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            str: The product reviews extracted from the HTML content. If the reviews cannot be found, it returns 'N/A'.
        """
        try:
            reviews = soup.select_one('.a-size-base').text if soup.select_one('.a-size-base') else None
            return reviews
        except Exception as e:
            logging.error(f"Error extracting product reviews: {str(e)}")
            return None

    def extract_product_url(self, soup):
        """
        Extracts the URL of a product from the given BeautifulSoup object.

        Parameters:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            str: The URL of the product. If the URL cannot be found, it returns 'N/A'. If an error occurs during extraction, it returns 'URL not found' and logs the error message.
        """
        try:
            product_url = soup.select_one('h2 a')['href'] if soup.select_one('h2 a') else None
            return f"https://www.amazon.com{product_url}" if product_url else None
        except Exception as e:
            logging.error(f"Error extracting product URL: {str(e)}")
            return None

    def extract_product_image_url(self, soup):
        """
        Extracts the product image URL from the given BeautifulSoup object.

        Parameters:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            str: The URL of the product image. If the image URL cannot be found, it returns 'Image URL not found'.
        """
        try:
            img_tag = soup.find('img', class_='s-image')
            if img_tag and 'src' in img_tag.attrs:
                return img_tag['src']
            return None
        except Exception as e:
            logging.error(f"Error extracting product image URL: {str(e)}")
            return None

    def get_next_page_url(self, soup):
        try:
            next_page = soup.select_one('.s-pagination-next')
            if next_page and 'href' in next_page.attrs:
                return f"https://www.amazon.com{next_page['href']}"
            return None
        except Exception as e:
            logging.error(f"Error finding next page URL: {str(e)}")
            return None

    def drop_placeholder_rows(self, product_data):
        try:
            return [product for product in product_data if all(value is not None for value in product.values())]
        except Exception as e:
            logging.error(f"Error dropping placeholder rows: {str(e)}")
            return product_data
    def scrape_page(self, url):
        try:
            html_text = self.fetch_html(url)
            if not html_text:
                return []

            soup = self.parse_html(html_text)
            if not soup:
                return []

            product_data = []
            items = soup.select('.s-result-item')

            for item in items:
                product_data.append({
                    "name": self.extract_product_name(item),
                    "price": self.extract_product_price(item),
                    "reviews": self.extract_product_reviews(item),
                    "product_url": self.extract_product_url(item),
                    "image_url": self.extract_product_image_url(item),
                })
                time.sleep(1)  # To avoid being blocked by Amazon
            return product_data
        except Exception as e:
            logging.error(f"Error scraping page: {str(e)}")
            return []
        
    def save_to_database(self, product_data):
        try:
            website, created = Website.objects.get_or_create(name='Amazon', url=self.base_url)
            for product in product_data:
                Product.objects.create(
                    name=product['name'],
                    price=product['price'],
                    reviews=product['reviews'],
                    url=product['product_url'],
                    image_url=product['image_url'],
                    website=website
                )
        except Exception as e:
            logging.error(f"Error saving to database: {str(e)}")
            
    def scrape(self):
        """
        Scrapes Amazon for product data and returns it as a pandas DataFrame.

        Returns:
            pandas.DataFrame: A DataFrame containing the scraped product data.
                The DataFrame has the following columns:
                - name (str): The name of the product.
                - price (str): The price of the product.
                - reviews (str): The number of reviews for the product.
                - product_url (str): The URL of the product page.
                - image_url (str): The URL of the product image.
        """
        all_product_data = []
        current_url = f"{self.base_url}{keyword}"
        try:
            for _ in range(self.max_pages):
                logging.info(f"Scraping page: {current_url}")
                product_data = self.scrape_page(current_url)
                if not product_data:
                    break
                all_product_data.extend(product_data)
                current_url = self.get_next_page_url(self.parse_html(self.fetch_html(current_url)))
                if not current_url:
                    break
            all_product_data = self.drop_placeholder_rows(all_product_data)
            self.save_to_database(all_product_data)
        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
    
# if __name__ == '__main__':
#     scraper = AmazonScraper('https://www.amazon.com/s?k=iphone', max_pages=5)
#     df_product = scraper.scrape()
